import click
import semver
from traitlets.config import default

import urnc.util as util


def bump(version, action):
    v = semver.Version.parse(version)
    match action:
        case "show":
            print(f"Current Version: {v}")
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
    config["project"]["version"] = str(new_version)
    util.write_pyproject(ctx, config)
    return


@click.command()
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
    v = semver.Version.parse(config["version"])
    print(v)

    print(action)
    print(config)
