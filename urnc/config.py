from ruamel.yaml import YAML
from pathlib import Path
from typing import Optional
import os
import click

from traitlets.config import Config

from urnc import logger


# Functions for reading/writing course configs


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


def read(root: Path) -> Config:
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
    filename = "config.yaml"
    config_path = find_file(root, filename)

    config = Config()
    config.base_path = root

    if not config_path or not os.path.isfile(config_path):
        logger.warn(f"No config.yaml found in {root} or its parent directories.")
        logger.warn("Using default config")
        return config

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    try:
        with open(config_path, "r") as f:
            config_data = yaml.load(f)
            config.merge(config_data)
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
        with open(config_path, "rw", newline="\n") as f:
            config_data = yaml.load(f)
            config_data["version"] = version
            yaml.dump(config_data, f)
    except Exception as e:
        raise click.FileError(str(config_path), str(e))


def resolve_path(config: Config, path: Path) -> Path:
    """
    Resolves a path relative to the course root.

    Args:
        config: The configuration dictionary.
        path: The path to resolve.

    Returns:
        The resolved absolute path.
    """
    if path.is_absolute():
        return path
    new_path = Path(config.base_path).joinpath(path)
    return new_path.resolve()
