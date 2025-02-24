"""Main entry point for urnc when called from command line"""

#!/usr/bin/env python3
import os
import sys
import click
import urnc
from urnc.convert import WriteMode, TargetType
from urnc.logger import log, warn


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
    config["convert"]["write_mode"] = WriteMode.OVERWRITE
    config["ci"]["commit"] = True
    urnc.ci.ci(config)


@click.command(help="Build and show the student version")
@click.pass_context
def student(ctx):
    config = ctx.obj
    config["convert"]["write_mode"] = WriteMode.OVERWRITE
    config["ci"]["commit"] = False
    urnc.ci.ci(config)


@click.command(
    name="convert",
    short_help="Convert notebooks",
    help="Convert notebooks to other versions. For details see https://spang-lab.github.io/urnc/urnc.html#urnc.convert.convert.",
)
@click.argument("input", type=click.Path(exists=True), default=".")
@click.option("-o", "--output", type=str, default=None)
@click.option("-s", "--solution", type=str, default=None)
@click.option("-f", "--force", is_flag=True)
@click.option("-n", "--dry-run", is_flag=True)
@click.option("-i", "--interactive", is_flag=True)
@click.pass_context
def convert(ctx, input, output, solution, force, dry_run, interactive):
    config = ctx.obj
    if sum([force, dry_run, interactive]) > 1:
        raise click.UsageError(
            "Only one of --force, --dry-run, --interactive can be set at a time."
        )
    config["convert"]["write_mode"] = WriteMode.SKIP_EXISTING
    if force:
        config["convert"]["write_mode"] = WriteMode.OVERWRITE
    if dry_run:
        config["convert"]["write_mode"] = WriteMode.DRY_RUN
    if interactive:
        if sys.stdout.isatty():
            config["convert"]["write_mode"] = WriteMode.INTERACTIVE
        else:
            raise click.UsageError(
                "Interactive mode is only available when stdout is a tty."
            )
    targets = []
    if output is not None:
        targets.append(
            {
                "type": TargetType.STUDENT,
                "path": output,
            }
        )
    if solution is not None:
        targets.append(
            {
                "type": TargetType.SOLUTION,
                "path": solution,
            }
        )

    if len(targets) == 0:
        warn("No targets specified for convert. Running check only.")
        config["convert"]["write_mode"] = WriteMode.DRY_RUN
        targets.append(
            {
                "type": TargetType.STUDENT,
                "path": None,
            }
        )
    input_path = urnc.config.resolve_path(config, input)
    urnc.convert.convert(config, input_path, targets)


@click.command(help="Check notebooks for errors")
@click.argument("input", type=click.Path(exists=True), default=".")
@click.pass_context
@click.option("-q", "--quiet", is_flag=True)
@click.option("-c", "--clear", is_flag=True)
@click.option("-i", "--image", is_flag=True)
def check(ctx, input, quiet, clear, image):
    config = ctx.obj
    input_path = urnc.config.resolve_path(config, input)
    if not quiet:
        urnc.logger.set_verbose()
    if clear:
        log("Clearing cell outputs")
        config["convert"]["write_mode"] = WriteMode.OVERWRITE
        targets = [
            {
                "type": TargetType.CLEAR,
                "path": "{nb.relpath}",
            }
        ]
        urnc.convert.convert(config, input_path, targets)
        return
    if image:
        log("Fixing image paths")
        config["convert"]["write_mode"] = WriteMode.OVERWRITE
        targets = [
            {
                "type": TargetType.FIX,
                "path": "{nb.relpath}",
            }
        ]
        urnc.convert.convert(config, input_path, targets)
        return

    config["convert"]["write_mode"] = WriteMode.DRY_RUN
    targets = [
        {
            "type": TargetType.STUDENT,
            "path": None,
        }
    ]
    urnc.convert.convert(config, input_path, targets)


@click.command(help="Execute notebooks")
@click.argument("input", type=click.Path(exists=True), default=".")
@click.option("-o", "--output", type=str, default=None)
@click.pass_context
def execute(ctx, input, output):
    config = ctx.obj
    config["convert"]["write_mode"] = WriteMode.SKIP_EXISTING
    targets = [
        {
            "type": TargetType.EXECUTE,
            "path": output,
        }
    ]
    input_path = urnc.config.resolve_path(config, input)
    urnc.convert.convert(config, input_path, targets)


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
    with urnc.util.chdir(ctx.obj["base_path"]):
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

    with urnc.util.chdir(ctx.obj["base_path"]):
        urnc.logger.setup_logger()
        try:
            urnc.pull.clone(git_url, output, branch, depth)
        except Exception as err:
            urnc.logger.error("clone failed with unexpected error.")
            urnc.logger.error(err)


@click.command(help="Init a new course")
@click.argument("name", type=str, required=True)
@click.pass_context
def init(ctx, name):
    config = ctx.obj
    urnc.init.init(config, name)


main.add_command(version)
main.add_command(convert)
main.add_command(ci)
main.add_command(check)
main.add_command(execute)
main.add_command(student)
main.add_command(pull)
main.add_command(clone)
main.add_command(init)
