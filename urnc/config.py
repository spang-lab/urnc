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

target_suffix: Dict[str, str] = {
    TargetType.STUDENT: "",
    TargetType.SOLUTION: "-solution",
    TargetType.EXECUTE: "-executed",
    TargetType.CLEAR: "-cleared",
    TargetType.FIX: "-fixed",
}

target_types = tuple(TargetType) # Can be used for checks like `assert x in target_types`


def merge_dict(source: Dict[Any, Any],
               target: Dict[Any, Any]) -> Dict[str, Any]:
    """Merge entries from {source} into {target}. Like `update_dict(old=target, new=source)`."""
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


def update_dict(old: Dict[str, Any],
                new: Dict[str, Any]) -> Dict[str, Any]:
    """Update dict {old} recursively with values from {new}."""
    for k, v in new.items():
        if isinstance(v, dict):
            old_val = old.get(k)
            if not isinstance(old_val, dict):
                old_val = {}
            old[k] = update_dict(old_val, v)
        else:
            old[k] = v
    return old


def default_config(root: Union[str,Path]) -> Dict[str, Any]:
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
        "base_path": Path(root).absolute(),
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
    path = path.resolve()
    for parent in [path] + list(path.parents):
        candidate = parent / filename
        if candidate.exists():
            return candidate
    return None


def read(root: Path) -> Dict[str, Any]:
    """
	DEPRECATED. Use `read_config()` instead.

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


def read_config(path: Union[str, Path], strict: bool = True) -> Dict[str, Any]:
    """
    1. Searches for config.yaml in {path} and its parent directories
    2. Reads config.yaml
    3. Updates the default config with the values read from config.yaml
    4. Returns the updated config

    Raises a click.FileError if reading 'config.yaml' fails
    Raises a click.UsageError if 'config.yaml' is not found and {strict} is True
    """
    config_path = find_file(Path(path), "config.yaml")
    if config_path:
        course_config = read_yaml(config_path)
        defaults = default_config(config_path.parent)
        config = update_dict(defaults, course_config)
        config["is_default"] = False
    elif strict:
        msg = f"config.yaml not found in {path} or its parent directories"
        raise click.UsageError(msg)
    else:
        config = default_config(path)
        config["is_default"] = True
    return config


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


def read_yaml(path: Path) -> Dict[str, Any]:
    yaml_reader = YAML(typ="rt")
    yaml_reader.preserve_quotes = True
    try:
        with open(path, "r") as f:
            return(yaml_reader.load(f))
    except Exception as e:
        raise click.FileError(str(path), str(e))

