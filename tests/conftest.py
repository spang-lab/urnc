# Pytest will import this file before running any tests and execute the function
# starting with pytest. The purpose of this file is to:
#
# 1. Add a command-line option `--runslow` for running tests. If this option is
#    provided when running pytest, all tests will run. If it's not provided,
#    tests marked as slow will be skipped. This is implemented as described here:
#    https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option.
#
# 2. Define helper functions that can be used during the tests.

import shutil
import re
import os
import re
from os import chmod, getcwd, listdir, makedirs, remove
from os.path import dirname, join, exists, isdir, normpath, getsize, isfile
from stat import S_IWRITE
from typing import List, Union, Callable, Optional
import git
import pytest


ur_git_url = os.environ.get("UR_GIT_URL", default = "git@git.uni-regensburg.de:") # 1)
# 1) In our github actions we set UR_GIT_URL to "https://{token_name}:{token_value}/git.uni-regensburg.de/". Locally, where we usually don't have a token defined, we use SSH by default.


def pytest_addoption(parser):
    """
    Add the --runslow option to the pytest command-line parser.
    The option is stored as a boolean value, with a default of False.
    """
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_configure(config):
    """
    Add a new marker named slow to the pytest configuration. This marker can be
    used to mark tests as slow.
    """
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    """
    Called after pytest has collected all the tests but before it starts running
    them. If the --runslow option is not provided, it marks all tests that have
    the slow keyword with the skip marker, which causes pytest to skip these
    tests.
    """
    if config.getoption("--runslow"):
        return
    else:
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def init_outputs_dir(test_module: str,
                     test_function: str,
                     test_case: str,
                     inputs: List[str] = [],
                     input_sources: List[Union[str, Callable]] = []) -> str:
    """
    Initialize the outputs directory for a specific test case.

    This function creates an outputs directory if it doesn't exist, removes any files in the directory
    that are not in the inputs list (excluding .gitignore), and copies input files to the workspace.

    Parameters:
        test_module: The name of the test module.
        test_function: The name of the test function.
        test_case: The name of the test case.
        inputs: List of input files for the test case.
        input_sources: List of source paths to be copied into the outputs directory.
            Paths should be relative to the root of the repository.
            Instead of a path, a function that takes a destination path as an argument can be provided.

    Returns:
        The path to the outputs directory.
    """
    urnc_root = get_urnc_root()
    outputs = f"{urnc_root}/tests/outputs/{test_module}/{test_function}/{test_case}"
    if not exists(outputs):
        makedirs(outputs)
    output_files = listdir(outputs)
    to_be_removed = set(output_files) - set(inputs) - set([".gitignore"])
    for file in to_be_removed:
        path = f"{outputs}/{file}"
        rmforce(path)
    for src, dst in zip(input_sources, inputs):
        if dst not in output_files:
            dst = normpath(f"{outputs}/{dst}")
            if isinstance(src, str):
                src = normpath(f"{urnc_root}/{src}")
                xcopy(src, dst)
            elif callable(src):
                src(dst)
    return outputs


def clone_urnc_example_course(path: str = "urnc-example-course",
                              hash: str = "9c277cdc7c7985f433f2c7f6fabcba1eefd2f844") -> git.Repo:
    """
    Initialize the urnc-example-course directory.

    This function clones the urnc-example-course repository if it doesn't exist,
    and checks out a specific commit. If the path exists and is not a git repository,
    it removes the path before cloning. After cloning, it removes any mention of
    ACCESS_TOKEN in the config.yaml file.

    Args:
        path (str, optional): The path where the repository will be cloned.
            Defaults to "urnc-example-course".
        hash (str, optional): The specific commit hash to checkout after cloning.
            Defaults to "9c277cdc7c7985f433f2c7f6fabcba1eefd2f844".

    Returns:
        git.Repo: The cloned git repository.

    Examples:
        repo = init_urnc_example_course()
        repo = init_urnc_example_course(path="urncExampleCourse", hash="9c277cdc7c7985f433f2c7f6fabcba1eefd2f844")
    """
    url = "https://github.com/spang-lab/urnc-example-course"
    repo = clone(path, url, hash)
    # Remove ACCESS_TOKEN mentioned in config.yaml, as it most likely is not set
    # in the environment of the person running the tests. Since we only need to
    # clone/pull/checkout during the tests, but not push, this is fine.
    yaml = open(f"{path}/config.yaml").read()
    yaml = yaml.replace("urncbot:{URNC_ACCESS_TOKEN_STUDENT_REPO}@", "")
    open(f"{path}/config.yaml", "w", newline = "\n").write(yaml)
    return (repo)


def clone_urnc_example_course_public(path: str = "urnc-example-course-public",
                                     hash: str = "38e5c1169266dd50f13912c0546779ddb2f71c3d"
                                     ) -> git.Repo:
    url = "https://github.com/spang-lab/urnc-example-course-public.git"
    repo = clone(path, url, hash)
    return repo


def clone_data_science(path: str = "data-science",
                       hash: str = "496cdba07c68d9e781fa837c82dd70576186dec4"  # 2024-01-01 (approx. 8 am)
                       ) -> git.Repo:
    url = f"{ur_git_url}fids/data-science.git"
    repo = clone(path, url, hash)
    return repo


def clone_data_science_student(path: str = "data-science-student",
                               hash: str = "9d66b436a882c40a0cf763fa4c363bfc633303b2"  # 2024-01-01 (approx. 8 am)
                               ) -> git.Repo:
    url = f"{ur_git_url}fids-public/data-science.git"
    repo = clone(path, url, hash)
    return repo


def clone_developer_skills(path: str = "developer-skills",
                           hash: str = "93a33b4b19747df66d818b70643ce5279956b195"  # 2024-01-01 (approx. 8 am)
                           ) -> git.Repo:
    url = f"{ur_git_url}fids/developer-skills.git"
    repo = clone(path, url, hash)
    return repo


def clone_developer_skills_student(path: str = "developer-skills-student",
                                   hash: str = "1c53c8cd032d69d9faabe8b9284587caa487b7e7"  # 2024-01-01 (approx. 8 am)
                                   ) -> git.Repo:
    url = f"{ur_git_url}fids-public/developer-skills.git"
    repo = clone(path, url, hash)
    return repo


def clone(path: str, url: str, hash: str) -> git.Repo:
    """
    Clone a git repository at a specific commit hash.

    This function clones a git repository from a given URL into a specified path,
    and checks out a specific commit. If the path exists and is not a git repository,
    it removes the path before cloning.

    Args:
        path (str): The path where the repository will be cloned.
        url (str): The URL of the git repository to clone.
        hash (str): The specific commit hash or branch name to checkout after cloning.

    Returns:
        git.Repo: The cloned git repository.

    Examples:
        repo = clone(path="./temp", url="https://github.com/spang-lab/urnc-example-course", hash="9c277cdc7c7985f433f2c7f6fabcba1eefd2f844")
    """
    if isdir(path) and not isdir(f"{path}/.git"):
        shutil.rmtree(path)
    if "https://git.uni-regensburg.de" in url and "UR_GIT_TOKEN" in os.environ:
        token = os.environ["UR_GIT_TOKEN"]
        url = url.replace(
            f"https://git.uni-regensburg.de",
            f"https://{token}@git.uni-regensburg.de"
        )
    if not isdir(path):
        git.Repo.clone_from(url=url, to_path=path)
    repo = git.Repo(path)
    repo.git.checkout(hash)
    return repo


def xcopy(src, dst):
    """
    Copy the source file or directory to the destination.

    If the source is a directory, this function will copy the entire directory tree.
    If the source is a file, it will just copy the file.

    Parameters:
        src (str): The source file or directory path.
        dst (str): The destination file or directory path.

    Examples:
        # Copy file xyz.txt into directory path/to/dst
        xcopy('path/to/src/xyz.txt', 'path/to/dst/xyz.txt')
        xcopy('path/to/src/xyz.txt', 'path/to/dst/')
        xcopy('path/to/src/xyz.txt', 'path/to/dst')
        # Copy directory abc into directory path/to/dst
        xcopy('path/to/src/abc', 'path/to/dst/')
        xcopy('path/to/src/abc', 'path/to/dst')
        # Attention: the following will copy directory `abc` into
        # `path/to/dst/abc`, not `path/to/dst`. I.e. the destination path will
        # `path/to/dst/abc/abc`.
        xcopy('path/to/src/abc', 'path/to/dst/abc')
    """
    if isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy(src, dst)


def rmforce(path):
    """
    Remove the specified path, regardless of whether it is a file or directory,
    and irrespective of its read-only status.
    """
    if isdir(path):
        rmtree(path)  # Remove directory and its contents
    else:
        remove(path)  # Remove file


def get_urnc_root():
    """
    This function navigates up the directory tree from the current working directory until it finds a 'pyproject.toml' file that belongs to the 'urnc' package, or it reaches the root directory. If it doesn't find a suitable    'pyproject.toml' file, it raises an Exception.

    Returns:
        str: The path of the directory containing the 'pyproject.toml' file of the 'urnc' package.

    Raises:
        Exception: If no 'pyproject.toml' file is found in the directory hierarchy.
        Exception: If the found 'pyproject.toml' file does not belong to the 'urnc' package.
    """
    path = getcwd()
    while path != dirname(path):  # Stop at the root directory
        pyproject_path = join(path, 'pyproject.toml')
        if exists(pyproject_path):
            pyproject = open(pyproject_path, 'r').read()
            if re.search(r'name\s*=\s*"?urnc"?', pyproject):
                return path
            else:
                raise Exception(f"Path '{path}' does not belong to the 'urnc' package")
        path = dirname(path)
    raise Exception("No 'pyproject.toml' found in the directory hierarchy")


def rmtree(path):
    """Remove a directory tree, even if it is read-only."""
    if isdir(path):
        shutil.rmtree(path, onerror=remove_readonly_attribute)
    assert not isdir(path), f"Failed to remove {path}"


def remove_readonly_attribute(func, path, _):
    "Helper function for rmtree. Clears the readonly bit and reattempts removal."
    chmod(path, S_IWRITE)
    func(path)


def disable_solution_generation(config_yaml_path: str = "config.yaml"):
    # Open the file
    yaml = open(config_yaml_path, 'r').read()
    yaml = re.sub(r'solution: .*', 'solution: null', yaml)
    open(config_yaml_path, 'w', newline = "\n").write(yaml)


def compare_dirs(x, y):
    import glob
    xs = set(glob.glob(f"**", recursive=True, root_dir=x))
    ys = set(glob.glob(f"**", recursive=True, root_dir=y))
    left_only = xs - ys
    right_only = ys - xs
    common_files = xs & ys
    common_dirs = set((d for d in common_files if isdir(join(x, d)) and isdir(join(y, d))))
    common_files = common_files - common_dirs
    diff_size = set((f for f in common_files if getsize(join(x, f)) != getsize(join(y, f))))
    same_size = common_files - diff_size
    return left_only, right_only, diff_size, same_size
