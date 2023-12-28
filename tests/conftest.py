# Pytest will import this file before running any tests and execute the function
# starting with pytest. The purpose of this file is to:
#
# 1. Add a command-line option `--runslow` for running tests. If this option is
#    provided when running pytest, all tests will run. If it's not provided,
#    tests marked as slow will be skipped. This is implemented as described here:
#    https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option.
#
# 2. Define helper functions that can be used during the tests.

import platform
import shutil
import re
from os import chmod, getcwd, listdir, makedirs, remove
from os.path import dirname, join, exists, isdir, normpath
from stat import S_IWRITE
from typing import List, Optional

import git
import pytest

# Configure pytest


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

# Helper functions and constants for tests


python = "python" if platform.system() == "Windows" else "python3"


def init_outputs_dir(test_module: str,
                     test_function: str,
                     test_case: str,
                     inputs: List[str] = [],
                     input_sources: List[str] = []) -> str:
    """
    Initialize the outputs directory for a specific test case.

    This function creates an outputs directory if it doesn't exist, removes any files in the directory
    that are not in the inputs list (excluding .gitignore), and copies input files to the workspace.

    Parameters:
        test_module: The name of the test module.
        test_function: The name of the test function.
        test_case: The name of the test case.
        inputs: List of input files for the test case.
        input_sources: List of source files to be copied into the outputs directory.

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


def clone_urnc_example_course(path: Optional[str] = "urnc-example-course",
                              hash: Optional[str] = "9c277cdc7c7985f433f2c7f6fabcba1eefd2f844") -> Optional[git.Repo]:
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
    open(f"{path}/config.yaml", "w").write(yaml)
    return (repo)


def clone_urnc_example_course_public(path: Optional[str] = "urnc-example-course-public",
                                     hash: Optional[str] = "38e5c1169266dd50f13912c0546779ddb2f71c3d"
                                     ) -> Optional[git.Repo]:
    url = "https://github.com/spang-lab/urnc-example-course-public.git"
    repo = clone(path, url, hash)
    return repo


def clone_data_science(path: Optional[str] = "data-science",
                       hash: Optional[str] = "15fc5e5234767b943c4771aef3455bc7af910fb7"  # 2023-12-21
                       ) -> Optional[git.Repo]:
    url = "git@git.uni-regensburg.de:fids/data-science.git"
    repo = clone(path, url, hash)
    return repo


def clone_data_science_student(path: Optional[str] = "data-science-student",
                               hash: Optional[str] = "dd00a7320446f461d2a02a801f54f46f304029ea"  # 2023-12-21
                               ) -> Optional[git.Repo]:
    url = "git@git.uni-regensburg.de:fids-public/data-science.git"
    repo = clone(path, url, hash)
    return repo


def clone_developer_skills(path: Optional[str] = "developer-skills",
                           hash: Optional[str] = "6a211eda1fb96d56a50ac0ae2f73e331f6a166ae"  # 2023-12-21
                           ) -> Optional[git.Repo]:
    url = "git@git.uni-regensburg.de:fids/developer-skills.git"
    repo = clone(path, url, hash)
    return repo


def clone_developer_skills_student(path: Optional[str] = "developer-skills-student",
                                   hash: Optional[str] = "dc36b54c46763300394db39f3bb976921ac80ba8"  # 2023-12-21
                                   ) -> Optional[git.Repo]:
    url = "git@git.uni-regensburg.de:fids-public/developer-skills.git"
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
        hash (str): The specific commit hash to checkout after cloning.

    Returns:
        git.Repo: The cloned git repository.

    Examples:
        repo = clone(path="./temp", url="https://github.com/spang-lab/urnc-example-course", hash="9c277cdc7c7985f433f2c7f6fabcba1eefd2f844")
    """
    if isdir(path) and not isdir(f"{path}/.git"):
        shutil.rmtree(path)
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
    This function navigates up the directory tree from the current working directory until it finds a 'pyproject.toml' 
    file that belongs to the 'urnc' package, or it reaches the root directory. If it doesn't find a suitable 
    'pyproject.toml' file, it raises an Exception.

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
