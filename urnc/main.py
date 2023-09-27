#!/usr/bin/env python3
import click
import os

from urnc.convert import check, convert
from urnc.version import version
from urnc.ci import ci


@click.group(help="urnc manages UR FIDS courses")
@click.option("-f", "--root", help="The course folder", default=os.getcwd())
@click.pass_context
def main(ctx, root):
    ctx.ensure_object(dict)
    ctx.obj["ROOT"] = root
    pass


main.add_command(version)
main.add_command(convert)
main.add_command(ci)
main.add_command(check)
