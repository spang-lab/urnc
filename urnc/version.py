import click

import semver
import urnc.logger as log

import urnc.util as util


def bump(version, action):
    v = semver.Version.parse(version)
    print(v)
    match action:
        case "show":
            return None
        case "patch":
            return v.bump_patch()
        case "minor":
            return v.bump_minor()
        case "major":
            return v.bump_major()
    raise click.UsageError("Invalid action")


def version_self(ctx, action):
    repo = util.get_git_repo(ctx)
    config = util.read_pyproject(ctx)
    v = config["project"]["version"]
    new_version = bump(v, action)
    if not new_version:
        return
    if repo is not None and repo.is_dirty():
        log.error(f"Repo is not clean, commit your changes before calling version")
        return
    log.log(f"    New Version: {new_version}")
    config["project"]["version"] = str(new_version)
    path = util.write_pyproject(ctx, config)
    if repo is not None:
        message = f"v{new_version}"
        log.log("Committing new version and tagging the commit...")
        repo.index.add(path)
        repo.index.commit(message)
        repo.create_tag(message, "HEAD", message)
        print("Done.")


def version_course(ctx, action):
    config = util.read_config(ctx)
    v = config["version"]
    new_version = bump(v, action)
    if not new_version:
        return
    print(f"    New Version: {new_version}")
    config["version"] = str(new_version)
    util.write_config(ctx, config)


@click.command(help="Manage the semantic version of your course")
@click.option("--self", is_flag=True, help="Echo the version of urnc")
@click.argument(
    "action",
    type=click.Choice(["show", "patch", "minor", "major"]),
    required=False,
    default="show",
)
@click.pass_context
def version(ctx, self, action):
    log.setup_logger(False, False)
    if self:
        version_self(ctx, action)
    else:
        version_course(ctx, action)


@click.command(help="Manage the semantic version of your course")
@click.pass_context
def tag(ctx):
    repo = util.get_git_repo(ctx)
    config = util.read_config(ctx)
    v = config["version"]
    tag = f"v{v}"
    if util.tag_exists(repo, tag):
        raise click.UsageError(
            f"Tag {tag} already exists. Make sure to increment the version in config.yaml."
        )
    repo.create_tag(tag, "HEAD", tag)
    log.log(f"Tagged the current commit with {tag}.")
