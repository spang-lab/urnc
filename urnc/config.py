from ruamel.yaml import YAML
from pathlib import Path
from typing import Optional
import os
import click
from enum import StrEnum


class WriteMode(StrEnum):
    DRY_RUN = "dry-run"
    OVERWRITE = "overwrite"
    INTERACTIVE = "interactive"
    SKIP_EXISTING = "skip-existing"


class TargetType(StrEnum):
    STUDENT = "student"
    SOLUTION = "solution"
    EXECUTE = "execute"
    CLEAR = "clear"
    FIX = "fix"


def merge_dict(source, target):
    for key in source:
        if (
            key in target
            and isinstance(source[key], dict)
            and isinstance(target[key], dict)
        ):
            merge_dict(source[key], target[key])
        else:
            target[key] = source[key]
    return target


def default_config(root) -> dict:
    """
    Create a default configuration object with the base path set to the root of the course.

    Args:
        root: The root directory of the course.

    Returns:
        config: The configuration dictionary.


    """
    config = {
        "version": None,
        "base_path": root,
        "convert": {
            "write_mode": WriteMode.SKIP_EXISTING,
            "ignore": [],
            "targets": [],
            "keywords": {
                "solution": ["solution"],
                "skeleton": ["skeleton"],
                "assignment": ["assignment"],
            },
            "tags": {
                "solution": "solution",
                "skeleton": "skeleton",
                "assignment": "assignment",
                "assignment-start": "assignment-start",
                "ignore": "ignore",
                "no-execute": "no-execute",
            },
        },
        "git": {
            "student": None,
            "output_dir": "out",
            "exclude": [],
        },
        "ci": {
            "commit": False,
        },
        "is_default": True,
    }
    return config


def find_file(path: Path, filename: str) -> Optional[Path]:
    """
    Finds a file in a given path or any of its parent directories.

    Args:
        path: The path to start the search from.
        filename: The name of the file to find.

    Returns:
        Optional[Path]: The path to the file if found, otherwise None.
    """
    while path != path.parent:
        if path.joinpath(filename).exists():
            return path.joinpath(filename)
        path = path.parent
    return None


def read(root: Path) -> dict:
    """
    Reads the configuration from a YAML file named 'config.yaml' located at the root of the git repository.

    Args:
        root: The root directory of the course. Defaults to the root of the git repository when called from within a git repository.

    Raises:
        click.UsageError: If the 'config.yaml' file does not exist in the git root folder.
        click.FileError: If there is an error reading the file or processing its content.

    Returns:
        dict: The configuration dictionary.
    """
    root = Path(root)
    config = default_config(root)
    filename = "config.yaml"
    config_path = find_file(root, filename)

    if not config_path or not os.path.isfile(config_path):
        return config

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    try:
        with open(config_path, "r") as f:
            config_data = yaml.load(f)
            config = merge_dict(config_data, config)
            config["is_default"] = False
            return config
    except Exception as e:
        raise click.FileError(str(config_path), str(e))


def write_version(root: Path, version: str):
    filename = "config.yaml"
    config_path = find_file(root, filename)
    if not config_path:
        raise click.UsageError(
            f"No {filename} found in {root} or its parent directories"
        )
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    try:
        with open(config_path, "r+", newline="\n") as f:
            config_data = yaml.load(f)
            config_data["version"] = version
            f.seek(0)
            yaml.dump(config_data, f)
    except Exception as e:
        raise click.FileError(str(config_path), str(e))


def resolve_path(config: dict, pathstr: Path) -> Path:
    """
    Resolves a path relative to the course root.

    Args:
        config: The configuration dictionary.
        path: The path to resolve.

    Returns:
        The resolved absolute path.
    """
    path = Path(pathstr)
    if path.is_absolute():
        return path
    new_path = Path(config["base_path"]).joinpath(path)
    return new_path.resolve()
