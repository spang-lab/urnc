import click
import semver

import urnc.util as util


def version_self(ctx):
    config = util.read_pyproject(ctx)
    v = config["project"]["version"]
    print(v)
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
        version_self(ctx)
        return
    config = util.read_config(ctx)
    v = semver.Version.parse(config["version"])
    print(v)

    print(action)
    print(config)
