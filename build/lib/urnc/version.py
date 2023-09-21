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


def version_self(ctx, action):
    config = util.read_pyproject(ctx)
    v = config["project"]["version"]
    new_version = bump(v, action)
    if not new_version:
        return
    print(f"    New Version: {new_version}")
    config["project"]["version"] = str(new_version)
    util.write_pyproject(ctx, config)
    return


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
    if self:
        version_self(ctx, action)
        return
    config = util.read_config(ctx)
    v = config["version"]
    new_version = bump(v, action)
    if not new_version:
        return
    print(f"    New Version: {new_version}")
    config["version"] = str(new_version)
    util.write_config(ctx, config)