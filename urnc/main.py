"""Main entry point for urnc when called from command line"""
#!/usr/bin/env python3
import click
import os

from urnc.convert import check, convert
from urnc.edit import edit
from urnc.student import student
from urnc.version import version, tag
from urnc.pull import pull
from urnc.ci import ci


@click.group(help="urnc manages UR FIDS courses ")
@click.option("-f", "--root", help="The course folder", default=os.getcwd())
@click.version_option(prog_name="urnc", message="%(version)s")
@click.pass_context
def main(ctx, root):
    ctx.ensure_object(dict)
    ctx.obj["ROOT"] = root
    pass


main.add_command(version)
main.add_command(convert)
main.add_command(ci)
main.add_command(check)
main.add_command(edit)
main.add_command(student)
main.add_command(pull)
main.add_command(tag)
