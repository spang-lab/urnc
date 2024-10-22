"""Manage the semantic version of your course"""

import click
import os
import semver
import urnc
import urnc.logger as log
import tomli_w

try:
    import tomllib
except Exception:
    tomllib = None


def get_urnc_repo():
    path = util.get_urnc_root()
    try:
        git_repo = git.Repo(path, search_parent_directories=False)
        return git_repo
    except Exception:
        raise click.UsageError(f"Path '{path}' is not a git repo")


def read_pyproject():
    if tomllib is None:
        raise click.UsageError("tomllib (python3.11) is required")
    filename = "pyproject.toml"
    base_path = util.get_urnc_root()
    path = os.path.join(base_path, filename)
    try:
        with open(path, "rb") as f:
            config = tomllib.load(f)
            return config
    except Exception as e:
        raise click.FileError(path, str(e))


def write_pyproject(data):
    filename = "pyproject.toml"
    base_path = util.get_urnc_root()
    path = os.path.join(base_path, filename)
    try:
        with open(path, "wb") as f:
            tomli_w.dump(data, f)
            return path
    except Exception as e:
        raise click.FileError(path, str(e))


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
            return
        case "patch":
            return v.bump_patch()
        case "minor":
            return v.bump_minor()
        case "major":
            return v.bump_major()
        case "prerelease":
            return v.bump_prerelease()
    raise click.UsageError("Invalid action")


def version_self(action: str) -> None:
    """Bump the version of the urnc project itself.

    :param action: The action to perform (show, patch, minor, major).
    """
    repo = get_urnc_repo()
    config = read_pyproject()
    v = config["project"]["version"]
    new_version = bump(v, action)
    if not new_version:
        return
    if repo is not None and repo.is_dirty():
        log.error("Repo is not clean, commit your changes before calling version")
        return
    log.log(f"New Version: {new_version}")
    config["project"]["version"] = str(new_version)
    path = write_pyproject(config)
    if repo is not None:
        message = f"v{new_version}"
        log.log("Committing new version and tagging the commit...")
        repo.index.add(path)
        repo.index.commit(message)
        repo.create_tag(message, "HEAD", message)
        print("Done.")


def version_course(action: str) -> None:
    """Bump the version of the course.

    :param action: The action to perform (show, patch, minor, major).
    """
    try:
        config = urnc.config.read()
    except Exception:
        raise click.UsageError(
            "Could not find a config.yaml in the current directory. Use 'urnc version --self' to get the version of urnc."
        )
    v = config["version"]
    new_version = bump(v, action)
    if new_version:
        print(f"New Version: {new_version}")
        config["version"] = str(new_version)
        util.write_config(config)
