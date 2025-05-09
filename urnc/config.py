from enum import Enum
from pathlib import Path
from typing import Any, Dict, Union, Optional

import click
import os
from ruamel.yaml import YAML


class WriteMode(str, Enum):
    DRY_RUN = "dry-run"
    OVERWRITE = "overwrite"
    INTERACTIVE = "interactive"
    SKIP_EXISTING = "skip-existing"


class TargetType(str, Enum):
    STUDENT = "student"
    SOLUTION = "solution"
    EXECUTE = "execute"
    CLEAR = "clear"
    FIX = "fix"


def merge_dict(source: Dict[Any, Any],
               target: Dict[Any, Any]) -> Dict[str, Any]:
    """Merge entries from {source} into {target} that are not already in {target}."""
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


def default_config(root: Path) -> Dict[str, Any]:
    """
    Create a default configuration object with 'base_path' set to {root}

    Args:
        root: The root directory of the course.

    Returns:
        config: The configuration dictionary.
    """
    config = {
        # Mandatory keys (must be set in {root}/config.yaml)
        "name": None,
        "semester": None,
        "version": None,
        "description": None,
        "authors": None,
        "version": None,
        # Dynamic keys (set at runtime by urnc.config.read())
        "base_path": root,
        "is_default": True,
        # Optional keys (here the defaults are important)        
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
            "push": False,
            "pull": False,
            "dry_run": True,
            "skip_existing": False,
            "skip_git": False
        },
        "jupyter": None
        #
        # TODO: why are the following values defined as config options? 
        # 
        # - ci.commit
        # - ci.push
        # - ci.pull
        # - ci.dry_run
        # - ci.skip_existing
        # - ci.skip_git
        # - convert.write_mode
        #
        # I can't think of any scenario where you would want to configure those
        # in the config.yaml. So I think if would be more intuitive to set them
        # as function arguments.
        # 
        # Let's dicuss this. For now I omit them in
        # docs/source/configuration.md.
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


def read(root: Path) -> Dict[str, Any]:
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


def resolve_path(config: Dict[str, Any],
                 pathstr: Union[str, Path]) -> Path:
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
