import click

import semver

import urnc.util as util


def bump(version, action):
    v = semver.Version.parse(version)
    print(f"Current Version: {v}")
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



def version_self(ctx, action, repo):
    config = util.read_pyproject(ctx)
    v = config["project"]["version"]
    new_version = bump(v, action)
    if not new_version:
        return 
    if repo is not None and repo.is_dirty():
        print(f"Repo is not clean, commit your changes before calling version")
        return 
    print(f"    New Version: {new_version}")
    config["project"]["version"] = str(new_version)
    util.write_pyproject(ctx, config)
    if repo is not None:
        message = f"v{new_version}"
        print("Committing new version and tagging the commit...")
        repo.index.add("*")
        repo.index.commit(message)
        repo.create_tag(message, "HEAD", message)
        print("Done.")



def version_course(ctx, action, repo):
    config = util.read_config(ctx)
    v = config["version"]
    new_version = bump(v, action)
    if not new_version:
        return 
    if repo is not None and repo.is_dirty():
        print(f"Repo is not clean, commit your changes before calling version")
        return
    print(f"    New Version: {new_version}")
    config["version"] = str(new_version)
    util.write_config(ctx, config)
    if repo is not None:
        message = f"v{new_version}"
        print("Committing new version and tagging the commit...")
        repo.index.add("*")
        repo.index.commit(message)
        repo.create_tag(message, "HEAD", message)
        print("Done.")


def get_repo(ctx, action, no_git):
    if(no_git or action == "show"):
        return None
    return util.get_git_repo(ctx)


@click.command(help="Manage the semantic version of your course")
@click.option("--no-git", is_flag=True, help="Do not make a git commit")
@click.option("--self", is_flag=True, help="Echo the version of urnc")
@click.argument(
    "action",
    type=click.Choice(["show", "patch", "minor", "major"]),
    required=False,
    default="show",
)
@click.pass_context
def version(ctx, no_git, self, action):
    repo = get_repo(ctx, action, no_git)
    if self:
        version_self(ctx, action, repo)
    else:
        version_course(ctx, action, repo)
