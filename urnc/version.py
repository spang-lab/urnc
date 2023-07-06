import click

import urnc.util as util


@click.command()
@click.option("--self", is_flag=True, help="Echo the version of urnc")
@click.argument(
    "action", type=click.Choice(["show", "patch", "minor", "major"]), required=False
)
def version(self, action):
    if self:
        print("1.0.0")
        return
    if action is None:
        action = "show"

    util.get_git_root()
    print(action)
