"""Main entry point for urnc when called from command line"""

#!/usr/bin/env python3
import os
import sys
from typing import Dict, Optional, Any, List
from pathlib import Path
import click
import urnc
from urnc.config import WriteMode, TargetType, target_types
from urnc.logger import log, warn

from typing import Callable

def try_call(
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any
) -> None:
    errorcode: int = kwargs.pop("errorcode", 1)
    assert isinstance(errorcode, int), "errorcode must be an integer"
    try:
        func(*args, **kwargs)
    except Exception as err:
        urnc.logger.error(str(err))
        sys.exit(errorcode)


@click.group(help="Uni Regensburg Notebook Converter")
@click.version_option(prog_name="urnc", message="%(version)s")
@click.option("-f", "--root", default=os.getcwd(), type=click.Path(path_type=Path),
              help="Root folder for resolving relative paths.")
@click.option("-v", "--verbose", is_flag=True,
              help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, root: Path, verbose: bool) -> None:
    ctx.ensure_object(dict)
    urnc.logger.setup_logger(verbose)
    ctx.obj["root"] = root


@click.command(
    help="Create and push the student version",
    epilog="See https://spang-lab.github.io/urnc/commands/ci.html for details."
)
@click.pass_context
def ci(ctx: click.Context) -> None:
    config = urnc.config.read_config(ctx.obj["root"], strict=True)
    config["convert"]["write_mode"] = WriteMode.OVERWRITE
    config["ci"]["commit"] = True
    try_call(urnc.ci.ci, config)


@click.command(
    help="Create the student version of your course",
    epilog="See https://spang-lab.github.io/urnc/commands/student.html for details."
)
@click.pass_context
def student(ctx: click.Context) -> None:
    config = urnc.config.read_config(ctx.obj["root"], strict=True)
    config["convert"]["write_mode"] = WriteMode.OVERWRITE
    config["ci"]["commit"] = False
    try_call(urnc.ci.ci, config)


@click.command(
    name="convert",
    help="Convert notebooks",
    epilog="See https://spang-lab.github.io/urnc/commands/convert.html for details."
)
@click.argument("input", type=click.Path(exists=True, path_type=Path), default=Path("."))
@click.option("-t", "--target", "targets", multiple=True,
              help="Conversion target. " +
                   "Either 'student', 'solution', 'execute', 'clear' or 'fix'. " +
                   "Can be used multiple times. " +
                   "Can contain an additional, colon-separated output path, " +
                   "e.g. 'student:./out' or 'solution:C:\\temp\\solutions'.")
@click.option("-o", "--output", type=str, default=None, help="Output path for student version.")
@click.option("-s", "--solution", type=str, default=None, help="Output path for solution version.")
@click.option("-f", "--force", is_flag=True, help="Overwrite existing files.")
@click.option("-n", "--dry-run", is_flag=True, help="Try conversion, but don't write to disk.")
@click.option("-i", "--interactive", is_flag=True, help="Ask before overwriting files.")
@click.pass_context
def convert(
    ctx: click.Context,
    input: Path,
    targets: tuple[str, ...],
    output: Optional[str],
    solution: Optional[str],
    force: bool,
    dry_run: bool,
    interactive: bool,
) -> None:

    config = urnc.config.read_config(ctx.obj["root"], strict=False)
    if sum([force, dry_run, interactive]) > 1:
        msg = "Only one of --force, --dry-run, --interactive can be set at a time."
        raise click.UsageError(msg)
    config["convert"]["write_mode"] = WriteMode.SKIP_EXISTING
    if force:
        config["convert"]["write_mode"] = WriteMode.OVERWRITE
    if dry_run:
        config["convert"]["write_mode"] = WriteMode.DRY_RUN
    if interactive:
        if sys.stdout.isatty():
            config["convert"]["write_mode"] = WriteMode.INTERACTIVE
        else:
            msg = "Interactive mode is only available when stdout is a tty."
            raise click.UsageError(msg)

    # Parse -t/--target arguments
    target_dict: Dict[str, Any] = dict()
    for t in targets:
        if ":" in t:
            typ, path = t.split(":", 1)
            typ = typ.strip().lower()
            path = path.strip()
        else:
            typ = t.strip().lower()
            path = "out"
        target_dict[typ] = path
        if typ not in target_types:
            raise click.UsageError(f"Unknown target type: {typ}")

    # Parse --output and --solution targets (potentially overwriting -t/--target)
    if output is not None:
        target_dict[TargetType.STUDENT] = output
    if solution is not None:
        target_dict[TargetType.SOLUTION] = solution

    # Set default target if none provided
    if len(target_dict) == 0:
        warn("No targets specified for convert. Running check only.")
        config["convert"]["write_mode"] = WriteMode.DRY_RUN
        target_dict[TargetType.STUDENT] = None

    # Convert to list of dictionaries as expected by convert
    target_list = [{"type": typ, "path": path}
                   for typ, path in target_dict.items()]

    input_path = urnc.config.resolve_path(config, os.path.abspath(input))
    urnc.convert.convert(config, input_path, target_list)


@click.command(help="Check notebooks for errors",
               epilog="See https://spang-lab.github.io/urnc/commands/check.html for details.")
@click.argument("input", type=click.Path(exists=True), default=".")
@click.option("-q", "--quiet", is_flag=True, help="Only show warnings and errors.")
@click.option("-c", "--clear", is_flag=True, help="Clear cell outputs.")
@click.option("-i", "--image", is_flag=True, help="Fix image paths.")
@click.pass_context
def check(
    ctx: click.Context,
    input: str,
    quiet: bool,
    clear: bool,
    image: bool,
) -> None:
    config = urnc.config.read_config(ctx.obj["root"], strict=False)
    input_path = urnc.config.resolve_path(config, os.path.abspath(input))
    if not quiet:
        urnc.logger.set_verbose()
    if clear:
        log("Clearing cell outputs")
        config["convert"]["write_mode"] = WriteMode.OVERWRITE
        targets = [{"type": TargetType.CLEAR, "path": "{nb.relpath}"}]
        urnc.convert.convert(config, input_path, targets)
        return
    if image:
        log("Fixing image paths")
        config["convert"]["write_mode"] = WriteMode.OVERWRITE
        targets = [{"type": TargetType.FIX, "path": "{nb.relpath}"}]
        urnc.convert.convert(config, input_path, targets)
        return

    config["convert"]["write_mode"] = WriteMode.DRY_RUN
    targets = [{"type": TargetType.STUDENT, "path": None}]
    urnc.convert.convert(config, input_path, targets)


@click.command(
    help="Execute notebooks",
    epilog="See https://spang-lab.github.io/urnc/commands/execute.html for details."
)
@click.argument("input", type=click.Path(exists=True), default=".")
@click.option("-o", "--output", type=str, default=None, help="Output path for executed notebook(s).")
@click.pass_context
def execute(ctx: click.Context, input: str, output: Optional[str]) -> None:
    config = urnc.config.read_config(ctx.obj["root"], strict=False)
    config["convert"]["write_mode"] = WriteMode.SKIP_EXISTING
    targets = [{"type": TargetType.EXECUTE, "path": output}]
    input_path = urnc.config.resolve_path(config, os.path.abspath(input))
    urnc.convert.convert(config, input_path, targets)


@click.command(
    help="Manage the semantic version of your course",
    epilog="See https://spang-lab.github.io/urnc/commands/version.html for details."
)
@click.option("--self", is_flag=True, help="Echo the version of urnc.")
@click.argument(
    "action",
    type=click.Choice(["show", "patch", "minor", "major", "prerelease"]),
    required=False,
    default="show",
)
@click.pass_context
def version(ctx: click.Context, self: bool, action: str) -> None:
    config = urnc.config.read_config(ctx.obj["root"], strict=True)
    if self:
        urnc.version.version_self(config, action)
    else:
        urnc.version.version_course(config, action)


@click.command(
    help="Pull and automatically merge local changes",
    epilog="See https://spang-lab.github.io/urnc/commands/pull.html for details."
)
@click.argument("git_url", type=str, default=None, required=False)
@click.option(
    "-o", "--output", type=str, help="Path of the output folder.", default=None
)
@click.option("-b", "--branch", help="The branch to pull. Default: main.", default="main")
@click.option("-d", "--depth", help="The depth for git fetch. Default: 1.", default=1)
@click.option(
    "-l", "--log-file", type=click.Path(path_type=Path), help="The path to the log file.", default=None
)
@click.pass_context
def pull(
    ctx: click.Context,
    git_url: Optional[str],
    output: Optional[str],
    branch: str,
    depth: int,
    log_file: Optional[Path],
) -> None:
    config = urnc.config.read_config(ctx.obj["root"], strict=False)
    if log_file:
        urnc.logger.add_file_handler(log_file)
    with urnc.util.chdir(config["base_path"]):
        try:
            urnc.pull.pull(git_url, output, branch, depth)
        except Exception as err:
            urnc.logger.error("pull failed with unexpected error.")
            urnc.logger.error(str(err))


@click.command(
    help="Clone or pull if output exists already",
    epilog="See https://spang-lab.github.io/urnc/commands/clone.html for details."
)
@click.argument("git_url", type=str, default=None, required=False)
@click.option(
    "-o", "--output", type=str, help="The name of the output folder.", default=None
)
@click.option("-b", "--branch", help="The branch to pull.", default="main")
@click.option("-d", "--depth", help="The depth for git fetch.", default=1)
@click.option(
    "-l", "--log-file", type=click.Path(path_type=Path), help="The path to the log file.", default=None
)
@click.pass_context
def clone(
    ctx: click.Context,
    git_url: Optional[str],
    output: Optional[str],
    branch: str,
    depth: int,
    log_file: Optional[Path],
) -> None:
    config = urnc.config.read_config(ctx.obj["root"])
    if log_file:
        urnc.logger.add_file_handler(log_file)
    with urnc.util.chdir(config["base_path"]):
        urnc.logger.setup_logger()
        try:
            urnc.pull.clone(git_url, output, branch, depth)
        except Exception as err:
            urnc.logger.error("clone failed with unexpected error.")
            urnc.logger.error(str(err))


dirPath = click.Path(file_okay=False, dir_okay=True,
                     writable=True, path_type=Path)


@click.command(
    help="Init a new course",
    epilog="See https://spang-lab.github.io/urnc/commands/init.html for details."
)
@click.argument("name", type=str, required=True)
@click.option("-p", "--path", type=dirPath, help="Output directory. Default is derived from NAME.", default=None)
@click.option("-u", "--url", type=str, help="Git URL for admin repository.", default=None)
@click.option("-s", "--student", type=str, help="Git URL for student repository.", default=None)
@click.option("-t", "--template", type=click.Choice(["minimal", "full"]),
              help="Template to use. Default is 'minimal' (default).", default="minimal")
@click.pass_context
def init(ctx: click.Context,
         name: str,
         path: Path,
         url: str,
         student: str,
         template: str) -> None:
    root = ctx.obj["root"]
    with urnc.util.chdir(root):
        urnc.init.init(name, path=path, url=url,
                       student_url=student, template=template)


main.add_command(version)
main.add_command(convert)
main.add_command(ci)
main.add_command(check)
main.add_command(execute)
main.add_command(student)
main.add_command(pull)
main.add_command(clone)
main.add_command(init)
