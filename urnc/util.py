"""Utility functions for urnc"""

import abc
import os
import re
from pathlib import Path
from typing import Optional

import click
import git
from ruamel.yaml import YAML

yaml = YAML(typ="rt")


# Git related functions


def git_folder_name(git_url):
    name = git_url.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def branch_exists(repo, branch):
    origin_branch = f"origin/{branch}"
    for ref in repo.references:
        if ref.name == branch or ref.name == origin_branch:
            return True
    return False


def tag_exists(repo, tag):
    ref = f"refs/tags/{tag}"
    try:
        repo.git.rev_parse("--quiet", "--verify", ref)
        return True
    except Exception:
        return False


def update_repo_config(repo):
    try:
        r = repo.config_reader()
        name = r.get_value("user", "name")
        email = r.get_value("user", "email")
        assert name is not None
        assert email is not None
        return
    except Exception:
        pass

    config_writer = repo.config_writer()
    config_writer.set_value("user", "name", "urnc")
    config_writer.set_value("user", "email", "urnc@spang-lab.de")
    config_writer.release()


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
            raise Exception(f"Path '{path}' does not belong to the 'urnc' package")
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

    def __init__(self, path):
        self.path = path
        self._old_cwd = []

    def __enter__(self):
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self._old_cwd.pop())
