from typing import List, Optional
from pathlib import Path
import os

import nbformat
import click
import fnmatch

import urnc
from urnc.logger import dbg, log, warn, critical
from urnc.format import format_path, is_directory_path
from urnc.config import WriteMode, TargetType

from traitlets.config import Config
from nbconvert.exporters.notebook import NotebookExporter
from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.check_outputs import CheckOutputs
from urnc.preprocessor.image import ImageChecker
from urnc.preprocessor.solutions import SolutionProcessor
from urnc.preprocessor.clear_outputs import ClearOutputs
from urnc.preprocessor.executor import ExecutePreprocessor
from urnc.preprocessor.clear_tagged import ClearTaggedCells


def find_notebooks(input: Path, output_path: Optional[Path]) -> List[Path]:
    notebooks = []
    if not input.is_dir():
        critical(f"Input path '{input}' is not a directory. Aborting.")
    for root, dirs, files in os.walk(input, topdown=True):
        dirs[:] = [d for d in dirs if not d[0] == "."]
        files[:] = [f for f in files if f.lower().endswith(".ipynb")]
        for file in files:
            path = Path(root).joinpath(file)
            if output_path in path.parents:
                log(f"Skipping notebook {path} because it is in the output directory.")
                continue
            notebooks.append(path)
    return sorted(notebooks)


def filter_notebooks(notebooks: List[Path], ignore_patterns: List[str]) -> List[Path]:
    filtered = []
    for nb in notebooks:
        ignore = False
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(nb.name, pattern):
                log(f"Ignoring notebook {nb} because it matches pattern '{pattern}'")
                ignore = True
                break
        if not ignore:
            filtered.append(nb)
    return filtered


def write_notebook(notebook, path: Optional[Path], config):
    write_mode = config["convert"]["write_mode"]
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
    converted_notebooks = []
    for target in targets:
        type = target.get("type", None)
        path = target.get("path", None)
        converted_notebooks.extend(convert_target(input, path, type, config))
    for body, output_path in converted_notebooks:
        write_notebook(body, output_path, config)


def create_nb_config(config: dict) -> Config:
    nb_config = Config()
    convert = config["convert"]
    keywords = convert["keywords"]
    tags = convert["tags"]

    nb_config.AddTags.assignment_keywords = keywords["assignment"]
    nb_config.AddTags.solution_keywords = keywords["solution"]
    nb_config.AddTags.assignment_tag = tags["assignment"]
    nb_config.AddTags.assignment_start_tag = tags["assignment-start"]
    nb_config.AddTags.solution_tag = tags["solution"]

    nb_config.ImageChecker.base_path = str(config["base_path"])
    nb_config.SolutionProcessor.solution_keywords = keywords["solution"]
    nb_config.SolutionProcessor.solution_tag = tags["solution"]
    nb_config.SolutionProcessor.skeleton_keywords = keywords["skeleton"]

    nb_config.ClearTaggedCells.tags = [tags["no-execute"]]
    return nb_config


def convert_target(input: Path, path: str, type: str, config: dict):
    jobs = []

    if input.is_file():
        out_file = format_path(input, path, input.parent)
        jobs.append((input, out_file))
    else:
        output_path = None
        if is_directory_path(path):
            output_path = config["base_path"].joinpath(path)
        input_notebooks = find_notebooks(input, output_path)
        input_notebooks = filter_notebooks(input_notebooks, config["convert"]["ignore"])
        for nb in input_notebooks:
            out_file = format_path(nb, path, input)
            jobs.append((nb, out_file))

    nb_config = create_nb_config(config)
    preprocessors = None
    if type == TargetType.STUDENT:
        preprocessors = [ImageChecker, AddTags, SolutionProcessor, ClearOutputs]
    elif type == TargetType.SOLUTION:
        nb_config.SolutionProcessor.output = "solution"
        preprocessors = [AddTags, SolutionProcessor, ClearOutputs]
    elif type == TargetType.EXECUTE:
        preprocessors = [
            ClearTaggedCells,
            ExecutePreprocessor,
            CheckOutputs,
            ClearOutputs,
        ]
    elif type == TargetType.CLEAR:
        preprocessors = [ClearOutputs]
    elif type == TargetType.FIX:
        nb_config.ImageChecker.interactive = True
        nb_config.ImageChecker.autofix = True
        preprocessors = [ImageChecker]

    if preprocessors is None:
        critical(f"Unknown target type '{type}' in 'convert.targets'. Aborting.")

    nb_config.NotebookExporter.preprocessors = preprocessors
    converter = NotebookExporter(config=nb_config)

    converted_notebooks = []
    for notebook_path, output_path in jobs:
        dbg(f"Converting {notebook_path} to {output_path}")
        filename = notebook_path.name
        print(f"\x1b[94m  ---   {filename}    --- \x1b[0m   \n")

        nb_node = nbformat.read(notebook_path, as_version=4)
        resources = {
            "path": notebook_path,
            "filename": filename,
        }
        body, resources = converter.from_notebook_node(nb_node, resources)
        converted_notebooks.append((body, output_path))
    return converted_notebooks
