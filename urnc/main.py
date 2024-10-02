"""Main entry point for urnc when called from command line"""

#!/usr/bin/env python3
import os
import click
import urnc
from pathlib import Path


@click.group(help="Uni Regensburg Notebook Converter")
@click.option(
    "-f",
    "--root",
    help="Root folder for resolving relative paths. E.g. `urnc -f some/long/path convert xyz.ipynb out` is the same as `urnc convert some/long/path/xyz.ipynb some/long/path/out`.",
    default=os.getcwd(),
    type=click.Path(),
)
@click.version_option(prog_name="urnc", message="%(version)s")
@click.pass_context
def main(ctx, root):
    ctx.ensure_object(dict)
    ctx.obj["root"] = root


@click.command(
    short_help="Build student version and push to public repo",
    help="Run the urnc ci pipeline, i.e. create student versions of all notebooks and push the converted notebooks to the public repo. To test the pipeline locally, without actually pushing to the remote, use command `urnc student`. For further details see https://spang-lab.github.io/urnc/urnc.html#urnc.ci.ci.",
)
@click.pass_context
def ci(ctx):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.ci.ci(True)


@click.command(
    name="convert",
    short_help="Convert notebooks",
    help="Convert notebooks to student version. For details see https://spang-lab.github.io/urnc/urnc.html#urnc.convert.convert.",
)
@click.argument("input", type=click.Path(exists=True), default=".")
@click.argument("output", type=str, default="out")
@click.option("-s", "--solution", type=str, default=None)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-f", "--force", is_flag=True)
@click.option("-n", "--dry-run", is_flag=True)
@click.pass_context
def convert(ctx, input, output, solution, verbose, force, dry_run):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger(False, verbose)
        urnc.convert.convert(input, output, solution, force, dry_run)


@click.command(help="Check notebooks for errors")
@click.argument("input", type=click.Path(exists=True), default=".")
@click.pass_context
@click.option("-q", "--quiet", is_flag=True)
def check(ctx, input, quiet):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger(use_file=False, verbose=not quiet)
        urnc.convert.convert(
            input=input,
            output=Path("out"),
            solution=None,
            force=False,
            dry_run=True,
            ask=False,
        )


@click.command(help="Manage the semantic version of your course")
@click.option("--self", is_flag=True, help="Echo the version of urnc")
@click.argument(
    "action",
    type=click.Choice(["show", "patch", "minor", "major", "prerelease"]),
    required=False,
    default="show",
)
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


@click.command(help="Pull the repo and automatically merge local changes")
@click.argument("git_url", type=str, default=None, required=False)
@click.option(
    "-o", "--output", type=str, help="The name of the output folder", default=None
)
@click.option("-b", "--branch", help="The branch to pull", default="main")
@click.option("-d", "--depth", help="The depth for git fetch", default=1)
@click.pass_context
def pull(ctx, git_url, output, branch, depth):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger()
        try:
            urnc.pull.pull(git_url, output, branch, depth)
        except Exception as err:
            urnc.logger.error("pull failed with unexpected error.")
            urnc.logger.error(err)


@click.command(help="Clone/Pull the repo")
@click.argument("git_url", type=str, default=None, required=False)
@click.option(
    "-o", "--output", type=str, help="The name of the output folder", default=None
)
@click.option("-b", "--branch", help="The branch to pull", default="main")
@click.option("-d", "--depth", help="The depth for git fetch", default=1)
@click.pass_context
def clone(ctx, git_url, output, branch, depth):
    with urnc.util.chdir(ctx.obj["root"]):
        urnc.logger.setup_logger()
        try:
            urnc.pull.clone(git_url, output, branch, depth)
        except Exception as err:
            urnc.logger.error("clone failed with unexpected error.")
            urnc.logger.error(err)


main.add_command(version)
main.add_command(convert)
main.add_command(ci)
main.add_command(check)
main.add_command(student)
main.add_command(pull)
main.add_command(clone)
main.add_command(tag)
