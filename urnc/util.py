"""Utility functions for urnc"""

import abc
import os
import re
from pathlib import Path
from typing import Optional

import click
import git
import tomli_w
from ruamel.yaml import YAML

try:
    import tomllib
except Exception:
    tomllib = None

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


def get_urnc_repo():
    path = get_urnc_root()
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


# Functions for reading/writing course configs


def read_config(course_root: Optional[Path] = None) -> dict:
    """
    Reads the configuration from a YAML file named 'config.yaml' located at the root of the git repository.

    Args:
        course_root: The root directory of the course. Defaults to the root of the git repository when called from within a git repository.

    Raises:
        click.UsageError: If the 'config.yaml' file does not exist in the git root folder.
        click.FileError: If there is an error reading the file or processing its content.

    Returns:
        dict: The configuration dictionary.
    """
    filename = "config.yaml"
    if course_root is None:
        course_root = get_course_root()
    path = os.path.join(course_root, filename)
    if not os.path.isfile(path):
        raise click.UsageError(
            f"urnc expects a config file called '{filename}' in the course root folder '{course_root}'"
        )
    try:
        with open(path, "r") as f:
            config = yaml.load(f)
        if "git" in config and "student" in config["git"]:
            config["git"]["student"] = config["git"]["student"].format(**os.environ)
    except Exception as e:
        raise click.FileError(path, str(e))
    return config


def write_config(data):
    filename = "config.yaml"
    base_path = get_course_root()

    path = os.path.join(base_path, filename)
    try:
        with open(path, "w", newline="\n") as f:
            yaml.dump(data, f)
            return path
    except Exception as e:
        raise click.FileError(path, str(e))


def get_config_value(config, *args, default=None, required=False):
    value = config
    full_key = "config"
    for key in args:
        full_key = f"{full_key}.{key}"
        if key not in value:
            if required:
                raise Exception(f"{full_key} is required")
            return default
        value = value[key]
    return value


def get_config_string(config, *args, default=None, required=False):
    value = get_config_value(config, *args, default=default, required=required)
    if value is None:
        return default
    if not isinstance(value, str):
        full_key = ".".join(args)
        raise Exception(f"config value config.{full_key} must be a string")
    return str(value)


# Functions for reading/writing urnc's pyproject.toml


def read_pyproject():
    if tomllib is None:
        raise click.UsageError("tomllib (python3.11) is required")
    filename = "pyproject.toml"
    base_path = get_urnc_root()
    path = os.path.join(base_path, filename)
    try:
        with open(path, "rb") as f:
            config = tomllib.load(f)
            return config
    except Exception as e:
        raise click.FileError(path, str(e))


def write_pyproject(data):
    filename = "pyproject.toml"
    base_path = get_urnc_root()
    path = os.path.join(base_path, filename)
    try:
        with open(path, "wb") as f:
            tomli_w.dump(data, f)
            return path
    except Exception as e:
        raise click.FileError(path, str(e))
