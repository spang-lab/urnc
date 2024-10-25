from typing import List, Optional
from pathlib import Path
import os
import sys

import nbformat
import click

from urnc.logger import log, warn, critical
from urnc.format import format_path
from urnc.config import WriteMode, TargetType

from traitlets.config import Config
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


def write_notebook(notebook, path: Optional[Path], config):
    write_mode = config.convert.write_mode
    if not path:
        return
    if write_mode == WriteMode.DRY_RUN:
        log(f"Would write notebook to {path}. Skipping, because dry_run is set.")
        return
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        if write_mode == WriteMode.OVERWRITE:
            log(f"Overwriting existing file {path}")
        elif write_mode == WriteMode.INTERACTIVE:
            if click.confirm(f"Overwrite existing file {path}?"):
                log(f"Overwriting existing file {path}")
            else:
                log(f"Skipping existing file {path}")
                return
        elif write_mode == WriteMode.SKIP_EXISTING:
            log(f"Skipping existing file {path}")
            return
        else:
            raise ValueError(f"Unknown write_mode '{write_mode}' in convert.config")

    with open(path, "w", newline="\n") as f:
        f.write(notebook)
        log(f"Wrote notebook to {path}")


def convert(config: dict, input: Path, targets: List[dict]):
    if len(targets) == 0:
        warn("No targets specified in convert.config. Exiting.")
        return
    for target in targets:
        type = target.get("type", None)
        path = target.get("path", None)
        convert_target(input, path, type, config)


def convert_target(input: Path, path: str, type: str, config: dict):
    jobs = []
    if input.is_file():
        out_file = format_path(input, path, input.parent)
        print(out_file)
        jobs.append((input, out_file))
    else:
        input_notebooks = find_notebooks(input)
        for nb in input_notebooks:
            out_file = format_path(nb, path, input)
            jobs.append((nb, out_file))

    preprocessors = None
    if type == TargetType.STUDENT:
        preprocessors = [Linter, AddTags, SolutionRemover, ClearOutputs]
    elif type == TargetType.SOLUTION:
        preprocessors = [AddTags, SkeletonRemover, ClearOutputs]
    else:
        critical(f"Unknown target type '{type}' in 'convert.targets'. Aborting.")
    if preprocessors is None:
        critical(f"Unknown target type '{type}' in 'convert.targets'. Aborting.")

    nb_config = Config()
    nb_config.NotebookExporter.preprocessors = preprocessors
    converter = NotebookExporter(config=nb_config)

    for notebook_path, output_path in jobs:
        nb_node = nbformat.read(notebook_path, as_version=4)
        resources = {
            "path": notebook_path,
        }
        body, resources = converter.from_notebook_node(nb_node, resources)
        write_notebook(body, output_path, config)
