"""Create student version from main version"""
import click
import re

import urnc.ci as ci


@click.command(help="Build and show the student version")
@click.pass_context
def student(ctx):
    ci.ci_fn(ctx, False)
