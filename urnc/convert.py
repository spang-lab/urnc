#!/usr/bin/env python3

import click
import nbformat
import re
import os
import sys
import enum
import inspect
from traitlets.config import Config
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from nbconvert.exporters.notebook import NotebookExporter


@click.command(help="Convert Notebooks for UR FIDS Courses")
@click.argument(
    "input",
    type=str,
    help="The input folder, it will be searched recursively",
)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def convert(ctx, input, verbose):
    parser.add_argument(
        "-i",
        "--ext",
        type=str,
        help="The output file extension, use '' for inplace conversion",
        default=".out",
    )
    parser.add_argument(
        "-f", "--force", help="Overwrite existing files", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose Log output", action="store_true"
    )

    paths = []
    if os.path.isfile(args.input):
        paths.append(args.input)
    else:
        for root, dirs, files in os.walk(args.input, topdown=True):
            dirs[:] = [d for d in dirs if not d[0] == "."]
            for file in files:
                if args.ext != "" and file.lower().endswith("%s.ipynb" % args.ext):
                    continue
                if file.lower().endswith(".ipynb"):
                    paths.append(os.path.join(root, file))

    if len(paths) == 0:
        print("No Notebooks found in input %s" % args.input)
        return

    c = Config()
    c.verbose = args.verbose
    c.NotebookExporter.preprocessors = [
        CheckAndAddTags,
        ProcessExercises,
        RemoveSolutions,
        ClearOutputPreprocessor,
    ]
    converter = NotebookExporter(config=c)

    for file in paths:
        (basepath, filename) = os.path.split(file)
        (basename, _) = os.path.splitext(filename)
        out_file = os.path.join(basepath, "%s%s.ipynb" % (basename, args.ext))
        if os.path.isfile(out_file):
            if not args.force:
                print("Skipping %s because %s already exists" % (file, out_file))
                continue
            else:
                print("Overwriting %s" % out_file)

        print("Converting '%s' into '%s'" % (file, out_file))
        notebook = nbformat.read(file, as_version=4)
        resources = {}
        resources["verbose"] = args.verbose
        (output, _) = converter.from_notebook_node(notebook, resources)

        with open(out_file, "w") as f:
            f.write(output)
