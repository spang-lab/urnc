"""Manage the semantic version of your course"""

import click

import semver
import urnc.logger as log

import urnc.util as util


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
    repo = util.get_urnc_repo()
    config = util.read_pyproject()
    v = config["project"]["version"]
    new_version = bump(v, action)
    if not new_version:
        return
    if repo is not None and repo.is_dirty():
        log.error("Repo is not clean, commit your changes before calling version")
        return
    log.log(f"New Version: {new_version}")
    config["project"]["version"] = str(new_version)
    path = util.write_pyproject(config)
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
        config = util.read_config()
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


def tag():
    """Tag the current commit with the current version of the course."""
    repo = util.get_course_repo()
    config = util.read_config()
    v = config["version"]
    tag = f"v{v}"
    if util.tag_exists(repo, tag):
        raise click.UsageError(
            f"Tag {tag} exists already. Make sure to increment the version in config.yaml."
        )
    repo.create_tag(tag, "HEAD", tag)
    log.log(f"Tagged the current commit with {tag}.")
