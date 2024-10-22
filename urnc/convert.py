from typing import List
from pathlib import Path
import os
import sys

import nbformat
import click
from traitlets.config import Config

from urnc.logger import log, warn, critical
from urnc.format import format_path

from nbconvert.exporters.notebook import NotebookExporter
from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.lint import Linter
from urnc.preprocessor.solutions import SolutionRemover, SkeletonRemover
from urnc.preprocessor.clear_outputs import ClearOutputs


def find_notebooks(input: Path) -> List[Path]:
    notebooks = []
    if not input.is_dir():
        critical(f"Input path '{input}' is not a directory. Aborting.")
    for root, dirs, files in os.walk(input, topdown=True):
        dirs[:] = [d for d in dirs if not d[0] == "."]
        files[:] = [f for f in files if f.lower().endswith(".ipynb")]
        for file in files:
            path = Path(root).joinpath(file)
            notebooks.append(path)
    return notebooks


def write_notebook(notebook, path, config):
    dry_run = config.get("convert.dry_run", False)
    if dry_run:
        log(f"Would write notebook to {path}. Skipping, because dry_run is set.")
        return

    ask = config.get("convert.ask", False)
    if not sys.stdout.isatty():
        warn("Not a tty. Skipping prompt.")
        ask = False

    force = config.get("convert.force", False)

    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        if force:
            log(f"Overwriting existing file {path}")
        elif ask:
            if click.confirm(f"Overwrite existing file {path}?"):
                log(f"Overwriting existing file {path}")
            else:
                log(f"Skipping existing file {path}")
                return
        else:
            log(f"Skipping existing file {path}")
            return

    with open(path, "w", newline="\n") as f:
        f.write(notebook)
        log(f"Wrote notebook to {path}")


def convert(config: Config):
    input = config.get("convert.input", None)
    if input is None:
        raise click.UsageError("No input specified in convert.config")
    targets = config.get("convert.targets", [])
    if len(targets) == 0:
        warn("No targets specified in convert.config. Exiting.")
        return

    for target in targets:
        type = target.get("type", None)
        path = target.get("path", None)
        convert_target(input, path, type, config)


def convert_target(input: Path, path: str, type: str, config: Config):
    jobs = []
    if input.is_file():
        out_file = format_path(input, path, input.parent)
        jobs.append((input, out_file))
    else:
        input_notebooks = find_notebooks(input)
        for nb in input_notebooks:
            out_file = format_path(nb, path, input)
            jobs.append((nb, out_file))

    preprocessors = None
    if type == "student":
        preprocessors = [Linter, AddTags, SolutionRemover, ClearOutputs]
    elif type == "solution":
        preprocessors = [AddTags, SkeletonRemover, ClearOutputs]
    if preprocessors is None:
        critical(f"Unknown target type '{type}' in 'convert.targets'. Aborting.")

    config.NotebookExporter.preprocessors = preprocessors
    converter = NotebookExporter(config=config)

    for notebook_path, output_path in jobs:
        nb_node = nbformat.read(notebook_path, as_version=4)
        resources = {
            "path": notebook_path,
        }
        body, resources = converter.from_notebook_node(nb_node, resources)
        write_notebook(body, output_path, config)
