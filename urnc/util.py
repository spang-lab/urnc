"""Utility functions for urnc"""

import abc
import filecmp
import os
import re
from pathlib import Path
from types import TracebackType
from typing import Optional, Union

import click
import git
import nbformat
from ruamel.yaml import YAML

from itertools import chain
import shutil
import stat
from typing import Callable, Any


yaml = YAML(typ="rt")


def _make_writeable(func: Callable[[str], Any], path: str, _: Any) -> None:
    """Helper of [rmtree()]. Makes {path} writeable, then calls 'func({path})'."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rmtree(path: Union[str, Path]) -> None:
    """Recursively delete a directory tree.

    Like [shutil.rmtree()] but also allows deletion of system files in Windows,
    like the .git folder created by GitPython during [urnc.init.init()].
    Implemented as shown in:
    https://docs.python.org/3/library/shutil.html#rmtree-example
    """
    shutil.rmtree(path, onerror=_make_writeable)


def dirs_equal(dir1: Union[str, Path],
               dir2: Union[str, Path],
               dotignore: bool = True) -> bool:
    """Return True if dir1 and dir2 are equal, False otherwise."""
    dir1 = Path(dir1)
    dir2 = Path(dir2)
    ignore = []
    if dotignore:
        files = chain(dir1.iterdir(), dir2.iterdir())
        ignore = list({f.name for f in files if f.name.startswith('.')})
    cmp = filecmp.dircmp(dir1, dir2, ignore=ignore)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    subdirs = cmp.common_dirs
    if dotignore:
        subdirs = [n for n in subdirs if not n.startswith('.')]
    for subdir in subdirs:
        if not dirs_equal(dir1/subdir, dir2/subdir, dotignore=dotignore):
            return False
    return True


def read_notebook(path: Union[str, Path]) -> nbformat.NotebookNode:
    with open(path, encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)


# Git related functions


def release_locks(repo: git.Repo) -> None:
    """Release system resources locked by GitPython.

    Required because GitPython leaves orphaned daemon processes with open file
    handles. On Unix-like systems, this is usually not a major issue, since
    such systems allow deletion of files even if they are still open by other
    processes. However, on Windows, this behavior prevents deletion of the .git
    folder (and any of its parent directories).

    For details see:
    - https://github.com/gitpython-developers/GitPython?tab=readme-ov-file#leakage-of-system-resources
    - https://github.com/gitpython-developers/GitPython/issues?q=label%3Atag.leaks

    Maybe we should switch to https://www.pygit2.org/index.html at some point
    in the future.
    """
    repo.git.clear_cache()
    repo.__del__()


def is_remote_git_url(url: str) -> bool:
    """Check if the given URL is pointing to a remote git repository."""
    url = url.strip()
    return (
        url.startswith(("http://", "https://", "git://", "ssh://")) or
        bool(re.match(r"^[\w\-]+@[\w\.\-]+:.*", url))
    )


def git_folder_name(git_url: str) -> str:
    name = git_url.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def branch_exists(repo: git.Repo, branch: str) -> bool:
    origin_branch = f"origin/{branch}"
    for ref in repo.references:
        if ref.name == branch or ref.name == origin_branch:
            return True
    return False


def tag_exists(repo: git.Repo, tag: str) -> bool:
    ref = f"refs/tags/{tag}"
    try:
        repo.git.rev_parse("--quiet", "--verify", ref)
        return True
    except Exception:
        return False


def ensure_git_identity(repo: git.Repo, force: bool = False):
    """Set user and email in .git/config if not set yet or force is True"""
    try:
        with repo.config_reader(config_level="repository") as config:
            name = config.get_value("user", "name")
            email = config.get_value("user", "email")
    except Exception:
        name = None
        email = None
    if name == None or email == None or force:
        with repo.config_writer(config_level="repository") as config:
            config.set_value("user", "name", "urnc")
            config.set_value("user", "email", "urnc@spang-lab.de")


update_repo_config = ensure_git_identity  # alias for backwards compatibility


def get_course_repo():
    path = get_course_root()
    try:
        git_repo = git.Repo(path, search_parent_directories=False)
        return git_repo
    except Exception:
        raise click.UsageError(f"Path '{path}' is not a git repo")


# Functions for finding/switching course/urnc root paths


def get_urnc_root():
    """
    This function navigates up the directory tree from the current working directory until it finds a 'pyproject.toml' file that belongs to the 'urnc' package, or it reaches the root directory. If it doesn't find a suitable    'pyproject.toml' file, it raises an Exception.

    Returns:
        str: The path of the directory containing the 'pyproject.toml' file of the 'urnc' package.

    Raises:
        Exception: If no 'pyproject.toml' file is found in the directory hierarchy.
        Exception: If the found 'pyproject.toml' file does not belong to the 'urnc' package.
    """
    path = Path(os.getcwd())
    while path != path.parent:
        pyproject_toml = path.joinpath("pyproject.toml")
        if pyproject_toml.exists():
            pyproject = open(pyproject_toml).read()
            if re.search(r'name\s*=\s*"?urnc"?', pyproject):
                return path
            errmsg = f"Path '{path}' does not belong to the 'urnc' package"
            raise Exception(errmsg)
        path = path.parent
    raise Exception("No 'pyproject.toml' found in the directory hierarchy")


def get_course_root() -> Path:
    """
    This function navigates up the directory tree from the current working directory until it finds a `config.yaml` file or it reaches the root directory. If it doesn't find a 'config.yaml' file, it raises an Exception.

    Returns:
        Path: path of the course directory.

    Raises:
        Exception: If no 'config.yaml' file is found in the directory hierarchy.
    """
    path = Path(os.getcwd())
    while path != path.parent:
        if path.joinpath("config.yaml").exists():
            return path
        path = path.parent
    raise Exception("No 'config.yaml' found in the directory hierarchy")


class chdir(abc.ABC):
    """Non thread-safe context manager to change the current working directory.

    Same as `contextlib.chdir <https://docs.python.org/3/library/contextlib.html#contextlib.chdir>`_. We implement it ourselves because ``contextlib.chdir`` is only available for python versions >=3.11 and we want to support versions >=3.8.

    Example:
        >>> with chdir(".."):
        >>>     # This code will be executed in the parent directory of the current working directory
        >>>     pass
    """

    def __init__(self, path: Union[str, Path]):
        self.path = path
        self._old_cwd = []

    def __enter__(self):
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self,
                 exc_type: Optional[type],
                 exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]):
        os.chdir(self._old_cwd.pop())
