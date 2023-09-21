import click
import nbformat
import re
import os
import sys
import enum
import inspect
from traitlets import default
from traitlets.config import Config
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from nbconvert.exporters.notebook import NotebookExporter

import urnc.preprocessor.add_tags as AddTags
import urnc.preprocessor.exercises as ProcessExercises
import urnc.preprocessor.remove_solutions as RemoveSolutions


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
@click.pass_context
def convert(ctx, input, output, verbose, force):
    paths = []
    folder = input
    if os.path.isfile(input):
        paths.append(input)
        folder = "."
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
        # AddTags,
        # ProcessExercises,
        # RemoveSolutions,
        ClearOutputPreprocessor,
    ]
    converter = NotebookExporter(config=c)

    for file in paths:
        opath = os.path.relpath(file, folder) 
        out_file = os.path.join(output, opath)
        (folder, _) = os.path.split(out_file)
        os.makedirs(folder, exist_ok=True)
        if os.path.isfile(out_file):
            if not force:
                print("Skipping %s because %s already exists" % (file, out_file))
                continue
            else:
                print("Overwriting %s" % out_file)

        print("Converting '%s' into '%s'" % (file, out_file))
        notebook = nbformat.read(file, as_version=4)
        resources = {}
        resources["verbose"] = verbose
        (output_text, _) = converter.from_notebook_node(notebook, resources)

        with open(out_file, "w") as f:
            f.write(output_text)
