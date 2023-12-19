"""Main entry point for urnc when called from command line"""
#!/usr/bin/env python3
import os

import click

import urnc


@click.group(help="Uni Regensburg Notebook Converter")
@click.option("-f", "--root", help="Root folder for resolving relative paths. E.g. `urnc -f some/long/path convert lecture_xyz.ipynb out` is the same as `urnc convert some/long/path/lecture_xyz.ipynb some/long/path/out`.", default=os.getcwd(), type=click.Path())
@click.version_option(prog_name="urnc", message="%(version)s")
@click.pass_context
def main(ctx, root):
    ctx.ensure_object(dict)
    ctx.obj["root"] = root


@click.command(short_help="Build student version and push to public repo", help="Run the urnc ci pipeline, this pushes the converted notebooks to the public repo")
@click.pass_context
def ci(ctx):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.ci.ci(True)


@click.command(short_help="Deprecated")
@click.pass_context
def edit(ctx):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.edit.edit()


@click.command(help="Convert notebooks")
@click.argument("input", type=click.Path(exists=True), default=".")
@click.argument("output", type=str, default="out")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-f", "--force", is_flag=True)
@click.option("-n", "--dry-run", is_flag=True)
@click.pass_context
def convert(ctx, input, output, verbose, force, dry_run):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger(False, verbose)
        urnc.convert.convert(input, output, force, dry_run)


@click.command(help="Check notebooks for errors")
@click.argument("input", type=click.Path(exists=True), default=".")
@click.pass_context
@click.option("-q", "--quiet", is_flag=True)
def check(ctx, input, quiet):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger(use_file=False, verbose=not quiet)
        urnc.convert.convert(ctx, input, None, False, True)


@click.command(help="Manage the semantic version of your course")
@click.option("--self", is_flag=True, help="Echo the version of urnc")
@click.argument("action", type=click.Choice(["show", "patch", "minor", "major"]), required=False, default="show")
@click.pass_context
def version(ctx, self, action):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger(use_file=False, verbose=False)
        if self:
            urnc.version.version_self(action)
        else:
            urnc.version.version_course(action)


@click.command(help="Tag the current commit with the current version of the course")
@click.pass_context
def tag(ctx):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.version.tag()


@click.command(help="Build and show the student version")
@click.pass_context
def student(ctx):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.ci.ci(commit=False)


@click.command(help="Pull the course repo")
@click.argument("course_name", type=str, default=None, required=False)
@click.option("-o", "--output", type=str, help="The name of the output folder", default=None)
@click.option("-b", "--branch", help="The branch to pull", default="main")
@click.option("-d", "--depth", help="The depth for git fetch", default=1)
@click.pass_context
def pull(ctx, course_name, output, branch, depth):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger()
        try:
            urnc.pull.pull(course_name, output, branch, depth)
        except Exception as err:
            urnc.logger.error("pull failed with unexpected error.")
            urnc.logger.error(err)


main.add_command(version)
main.add_command(convert)
main.add_command(ci)
main.add_command(check)
main.add_command(edit)
main.add_command(student)
main.add_command(pull)
main.add_command(tag)
