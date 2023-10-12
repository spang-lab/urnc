from os.path import abspath
import click
import nbformat
import os
from traitlets.config import Config
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from nbconvert.exporters.notebook import NotebookExporter

from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.assignments import ProcessAssignments
from urnc.preprocessor.remove_solutions import RemoveSolutions
from urnc.preprocessor.broken_links import BrokenLinks

import urnc.logger as log


@click.command(help="Convert Notebooks for UR FIDS Courses")
@click.argument(
    "input",
    type=click.Path(exists=True),
    default="."
)
@click.argument(
    "output",
    type=str,
    default="out"
)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-f", "--force", is_flag=True)
@click.option("-n", "--dry-run", is_flag=True)
@click.pass_context
def convert(ctx, input, output, verbose, force, dry_run):
    log.setup_logger(False, verbose)
    convert_fn(ctx, input, output, verbose, force, dry_run)


@click.command(help="Check Notebooks for errors")
@click.argument(
    "input",
    type=click.Path(exists=True),
    default="."
)
@click.pass_context
def check(ctx, input):
    log.setup_logger(False, True)
    convert_fn(ctx, input, None, True, False, True)


def get_abs_path(ctx, path):
    if (path is None):
        return None
    if (os.path.isabs(path)):
        return path
    base: str = ctx.obj["ROOT"]
    new_path = os.path.join(base, path)
    return os.path.abspath(new_path)


def convert_fn(ctx, input, output, verbose, force, dry_run):
    input = get_abs_path(ctx, input)
    if (input is None):
        raise Exception("No input")
    output = get_abs_path(ctx, output)
    print(f"Converting notebooks in {input} to {output}")
    paths = []
    folder = input
    if os.path.isfile(input):
        paths.append(input)
        folder = os.path.dirname(input)
    else:
        for root, dirs, files in os.walk(input, topdown=True):
            dirs[:] = [d for d in dirs if not d[0] == "."]
            for file in files:
                if file.lower().endswith(".ipynb"):
                    paths.append(os.path.join(root, file))

    if len(paths) == 0:
        print("No Notebooks found in input %s" % input)
        return

    c = Config()
    c.verbose = verbose
    c.NotebookExporter.preprocessors = [
        BrokenLinks,
        AddTags,
        ProcessAssignments,
        RemoveSolutions,
        ClearOutputPreprocessor,
    ]
    converter = NotebookExporter(config=c)

    for file in paths:
        opath = os.path.relpath(file, folder)
        out_file = None
        out_dir = None
        if output is not None:
            out_file = os.path.join(output, opath)
            out_dir = os.path.dirname(out_file)
            os.makedirs(out_dir, exist_ok=True)
        if out_file is None:
            print(f"Checking {file}")
        elif os.path.isfile(out_file):
            if not force:
                print(f"Skipping {file} because {out_file} already exists")
                continue
            else:
                print(f"Overwriting {out_file}")
        else:
            print(f"Converting '{file}' into '{out_file}'")
        notebook = nbformat.read(file, as_version=4)
        resources = {}
        resources["verbose"] = verbose
        resources["path"] = file
        (output_text, _) = converter.from_notebook_node(notebook, resources)

        if (out_file is None or dry_run):
            continue
        with open(out_file, "w") as f:
            f.write(output_text)
