#!/usr/bin/env python3
import click
import os

from urnc.version import version
import urnc.preprocessor.util


@click.group()
@click.option("-f", "--root", help="The course folder", default=os.getcwd())
@click.pass_context
def main(ctx, root):
    ctx.ensure_object(dict)
    ctx.obj["ROOT"] = root
    pass


main.add_command(version)
