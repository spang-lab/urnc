"""Main entry point for urnc when called from command line"""

#!/usr/bin/env python3
import os
import click
from traitlets.config import Config
import urnc
from urnc import logger


@click.group(help="Uni Regensburg Notebook Converter")
@click.version_option(prog_name="urnc", message="%(version)s")
@click.option(
    "-f",
    "--root",
    help="Root folder for resolving relative paths. E.g. `urnc -f some/long/path convert xyz.ipynb out` is the same as `urnc convert some/long/path/xyz.ipynb some/long/path/out`.",
    default=os.getcwd(),
    type=click.Path(),
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx, root, verbose):
    ctx.ensure_object(dict)
    config = urnc.config.read(root)
    urnc.logger.setup_logger(verbose)
    ctx.obj = config


@click.command(
    short_help="Build student version and push to public repo",
    help="Run the urnc ci pipeline, i.e. create student versions of all notebooks and push the converted notebooks to the public repo. To test the pipeline locally, without actually pushing to the remote, use command `urnc student`. For further details see https://spang-lab.github.io/urnc/urnc.html#urnc.ci.ci.",
)
@click.pass_context
def ci(ctx):
    config = ctx.obj
    config.convert.force = True
    config.convert.dry_run = False
    config.convert.ask = False
    config.ci.commit = True
    urnc.ci.ci(config)


@click.command(help="Build and show the student version")
@click.pass_context
def student(ctx):
    config = ctx.obj
    config.convert.force = True
    config.convert.dry_run = False
    config.convert.ask = False
    config.ci.commit = False
    urnc.ci.ci(config)


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
        config = urnc.util.get_config()
        cli_config = {
            "force": force,
            "dry_run": dry_run,
            "ask": True,
        }
        config["cli"] = cli_config
        urnc.convert.convert(input, output, solution, config)


@click.command(help="Check notebooks for errors")
@click.argument("input", type=click.Path(exists=True), default=".")
@click.pass_context
@click.option("-q", "--quiet", is_flag=True)
def check(ctx, input, quiet):
    config = ctx.obj
    config.convert.dry_run = True
    targets = [
        {
            "type": "student",
            "path": None,
        }
    ]

    input_path = urnc.config.resolve_path(config, input)
    urnc.convert.convert(config, input_path, targets)

    if not quiet:
        logger.set_verbose()


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
    config = ctx.obj
    if self:
        urnc.version.version_self(config, action)
    else:
        urnc.version.version_course(config, action)


@click.command(help="Pull the repo and automatically merge local changes")
@click.argument("git_url", type=str, default=None, required=False)
@click.option(
    "-o", "--output", type=str, help="The name of the output folder", default=None
)
@click.option("-b", "--branch", help="The branch to pull", default="main")
@click.option("-d", "--depth", help="The depth for git fetch", default=1)
@click.option(
    "-l", "--log-file", type=click.Path(), help="The path to the log file", default=None
)
@click.pass_context
def pull(ctx, git_url, output, branch, depth, log_file):
    if log_file:
        urnc.logger.add_file_handler(log_file)
    with urnc.util.chdir(ctx.obj["root"]):
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
@click.option(
    "-l", "--log-file", type=click.Path(), help="The path to the log file", default=None
)
@click.pass_context
def clone(ctx, git_url, output, branch, depth, log_file):
    if log_file:
        urnc.logger.add_file_handler(log_file)

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
