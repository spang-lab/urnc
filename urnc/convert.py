"""Create student version of one or more Jupyter notebooks"""

import os

import nbformat
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from traitlets.config import Config

import urnc.logger as log
from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.lint import Linter
from urnc.preprocessor.remove_solutions import RemoveSolutions


def convert(input: str = ".",
            output: str = "out/",
            force: bool = False,
            dry_run: bool = False) -> None:
    """Convert notebooks.

    Args:
        input: The input path. Can be either the path to a single ipynb file or the path to a directory containing ipynb files.
        output: The output path. Must be a directory. Every input notebook will be copied to the output directory and converted there. If the output directory does not exist, it will be created.
        force: If true, existing output files will be overwritten.
        dry_run: If true, input files will be converted but not written to disk. This is useful for checking if the conversion works without changing any files.

    Examples:
        convert_notebooks("/path/to/notebooks", "/path/to/output", force=True)
        convert_notebooks("/path/to/single_notebook.ipynb", "/path/to/output", dry_run=True)
    """
    log.log(f"Converting notebooks in {input} to {output}")
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
        log.warn("No notebooks found in input %s" % input)
        return

    c = Config()
    c.NotebookExporter.preprocessors = [
        Linter,
        AddTags,
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
            log.log(f"Checking {file}")
        elif os.path.isfile(out_file):
            if not force:
                log.log(f"Skipping {file} because {out_file} already exists")
                continue
            else:
                log.log(f"Overwriting {out_file}")
        else:
            log.log(f"Converting '{file}' into '{out_file}'")
        notebook = nbformat.read(file, as_version=4)
        resources = {}
        resources["path"] = file
        (output_text, _) = converter.from_notebook_node(notebook, resources)

        if (out_file is None or dry_run):
            continue
        with open(out_file, "w") as f:
            f.write(output_text)
