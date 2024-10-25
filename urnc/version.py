"""Manage the semantic version of your course"""

import click
import semver
import urnc
import re
from urnc.logger import log
from pathlib import Path


def bump(version: str, action: str):
    """Bump the version based on the action

    :param version: The current version.
    :param action: The action to perform (show, patch, minor, major, prerelease).
    :return: The new version after bumping, or None if action is 'show'.
    """
    v = semver.Version.parse(version)
    print(v)
    match action:
        case "show":
            return None
        case "patch":
            return str(v.bump_patch())
        case "minor":
            return str(v.bump_minor())
        case "major":
            return str(v.bump_major())
        case "prerelease":
            return str(v.bump_prerelease())
    raise click.UsageError("Invalid action")


def read_pyproject_version(path: Path):
    version_pattern = r'version = "(?P<version>.*)"'
    with open(path, "r") as f:
        for line in f:
            match = re.search(version_pattern, line)
            if match:
                return str(match.group("version"))
    raise click.UsageError("No version field found in pyproject.toml")


def write_pyproject_version(path: Path, version: str):
    version_pattern = r'version = "(?P<version>.*)"'
    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w", newline="\n") as f:
        for line in lines:
            match = re.search(version_pattern, line)
            if match:
                line = f'version = "{version}"\n'
            f.write(line)


def version_self(config: dict, action: str) -> str:
    """Bump the version of the urnc project itself.

    :param config: The configuration object.
    :param action: The action to perform (show, patch, minor, major).
    """
    base_path = config["base_path"]
    pyproject = base_path.joinpath("pyproject.toml")
    if not pyproject.is_file():
        raise click.UsageError(f"No pyproject.toml found in {base_path}")
    version = read_pyproject_version(pyproject)
    new_version = bump(version, action)
    if not new_version:
        return version
    repo = urnc.git.get_repo(base_path)
    if not repo:
        raise click.UsageError(f"Current path {base_path} is not a git repo")
    if repo.is_dirty():
        raise click.UsageError(
            "Repo is dirty, commit your changes before calling version"
        )
    print(f"New Version: {new_version}")
    write_pyproject_version(pyproject, new_version)

    log("Committing new version and tagging the commit...")
    message = f"v{new_version}"
    repo.index.add(str(pyproject))
    repo.index.commit(message)
    repo.create_tag(message, "HEAD", message)
    log("Done.")
    return new_version


def version_course(config: dict, action: str) -> str:
    """Bump the version of the course.

    :param config: The configuration object.
    :param action: The action to perform (show, patch, minor, major).
    """
    base_path = config["base_path"]
    config = urnc.config.read(base_path)

    v = config["version"]
    if v is None:
        raise click.UsageError(
            "No config.yaml found or no version field in config.yaml"
            f'urnc requires a config.yaml file in the current folder "{base_path}" (or its parents) '
            "with a version field to manage versions"
        )
    v = config["version"]
    new_version = bump(v, action)
    if not new_version:
        return v
    print(f"New Version: {new_version}")
    urnc.config.write_version(base_path, new_version)
    return new_version
