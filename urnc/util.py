"""Utility functions for urnc"""
import abc
import click
from ruamel import yaml
from ruamel.yaml import YAML
import tomli_w
import git
import os
import re
try:
    import tomllib
except:
    tomllib = None

yaml = YAML(typ='rt')


def branch_exists(repo, branch):
    origin_branch = f"origin/{branch}"
    for ref in repo.references:
        if (ref.name == branch or ref.name == origin_branch):
            return True
    return False


def update_repo_config(repo):
    try:
        r = repo.config_reader()
        name = r.get_value("user", "name")
        email = r.get_value("user", "email")
        assert (name is not None)
        assert (email is not None)
        return
    except Exception:
        pass

    config_writer = repo.config_writer()
    config_writer.set_value("user", "name", "urnc")
    config_writer.set_value("user", "email", "urnc@spang-lab.de")
    config_writer.release()


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


def get_git_repo():
    path = os.getcwd()
    try:
        git_repo = git.Repo(path, search_parent_directories=True)
        return git_repo
    except Exception:
        raise click.UsageError(f"Path '{path}' is not a git repo")


def tag_exists(repo, tag):
    ref = f"refs/tags/{tag}"
    try:
        repo.git.rev_parse("--quiet", "--verify", ref)
        return True
    except Exception:
        return False


def get_git_root():
    repo = get_git_repo()
    return repo.working_dir


def read_config():
    filename = "config.yaml"
    base_path = get_git_root()
    path = os.path.join(base_path, filename)
    if not os.path.isfile(path):
        raise click.UsageError(
            f"urnc expects a config file called '{filename}' in the git root folder '{base_path}' of the course")
    try:
        with open(path, "r") as f:
            config = yaml.load(f)
        if "git" in config and "student" in config["git"]:
            config["git"]["student"] = config["git"]["student"].format(**os.environ)
        return config
    except Exception as e:
        raise click.FileError(path, str(e))


def write_config(data):
    filename = "config.yaml"
    base_path = get_git_root()

    path = os.path.join(base_path, filename)
    try:
        with open(path, "w") as f:
            yaml.dump(data, f)
            return path
    except Exception as e:
        raise click.FileError(path, str(e))


def read_pyproject():
    if tomllib is None:
        raise click.UsageError("tomllib (python3.11) is required")
    filename = "pyproject.toml"
    base_path = get_git_root()

    path = os.path.join(base_path, filename)

    try:
        with open(path, "rb") as f:
            config = tomllib.load(f)
            return config
    except Exception as e:
        raise click.FileError(path, str(e))


def write_pyproject(data):
    filename = "pyproject.toml"
    base_path = get_git_root()

    path = os.path.join(base_path, filename)
    try:
        with open(path, "wb") as f:
            tomli_w.dump(data, f)
            return path
    except Exception as e:
        raise click.FileError(path, str(e))


class chdir(abc.ABC):
    """Non thread-safe context manager to change the current working directory.

    Same as [contextlib.chdir](https://docs.python.org/3/library/contextlib.html#contextlib.chdir). We implement it ourselves because `contextlib.chdir` is only available for python versions >=3.11 and we want to support versions >=3.8."""

    def __init__(self, path):
        self.path = path
        self._old_cwd = []

    def __enter__(self):
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self._old_cwd.pop())
