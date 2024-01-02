"""Create student version of one or more Jupyter notebooks"""

import os
from pathlib import Path
from typing import List, Optional, Union

import nbformat
import traitlets
import sys
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from traitlets.config import Config

import urnc.logger as log
from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.lint import Linter
from urnc.preprocessor.remove_solutions import RemoveSolutions


def convert(input: str = ".",
            output: str = "out/",
            solution: Optional[str] = None,
            force: bool = False,
            dry_run: bool = False) -> None:
    """Convert notebooks.

    Args:
        input: The input path. Can be either the path to a single ipynb file or the path to a directory containing ipynb files.
        output: Path for storing the student notebooks with solutions removed. Directories will be created if necessary. If `output` is None, the conversion will be skipped. Supports the following placeholder variables: `nb_path`, `nb_dir`, `nb_root`, `nb_relpath`, `nb_dir_relpath`, `nb_name`, `nb_basename`, `nb_ext`. For details see section "Details" below.
        solution: Path for storing the student notebooks with solutions. Directories will be created if necessary. If `solution` is None, the conversion will be skipped. Supports the following placeholder variables: `nb_path`, `nb_dir`, `nb_root`, `nb_relpath`, `nb_dir_relpath`, `nb_name`, `nb_basename`, `nb_ext`. For details see section "Details" below.
        force: If true, existing output files will be overwritten.
        dry_run: If true, input files will be converted but not written to disk. This is useful for checking if the conversion works without changing any files.

    Examples:
        convert("/path/to/single_notebook.ipynb", "/path/to/output", dry_run=True)
        convert("/path/to/notebooks", "/path/to/output", force=True)

    Details:
        A call like `convert("C:/Users/max/mycourse", ...)` will search `C:/Users/max/mycourse` recursively for notebooks and convert each notebook to student versions. To be able to specify output paths in a simple yet flexible way, the following placeholders are provided: `nb_path`, `nb_dir`, `nb_root`, `nb_relpath`, `nb_dir_relpath`, `nb_name`, `nb_basename`, `nb_ext`. To understand what these variables mean, consider the following folder structure:

        C:/Users/max/mycourse
        ├── lectures
        │   ├── week1
        │   │   ├── lecture1.ipynb
        │   │   └── lecture2.ipynb
        │   └── week2
        │       ├── lecture3.ipynb
        │       └── lecture4.ipynb
        └── assignments
            ├── week1.ipynb
            └── week2.ipynb

        The above course contains the following six notebooks, lecture1.ipynb, lecture2.ipynb, lecture3.ipynb, lecture4.ipynb, week1.ipynb and week2.ipynb. The following table shows the value of each placeholder variable exemplarily for notebook `C:/Users/max/mycourse/lectures/week2/lecture1.ipynb`:

        | nb_path        | C:/Users/max/mycourse/lectures/week2/lecture1.ipynb |
        | nb_dir         | C:/Users/max/mycourse/lectures/week2                |
        | nb_root        | C:/Users/max/mycourse                               |
        | nb_relpath     |                       lectures/week2/lecture1.ipynb |
        | nb_dir_relpath |                       lectures/week2/               |
        | nb_name        |                                      lecture1.ipynb |
        | nb_basename    |                                      lecture1       |
        | nb_ext         |                                               ipynb |

        I.e. the following function call

        convert(
            input = "C:/Users/max/mycourse",
            output = "C:/converted/{nb_relpath}",
            solution = "C:/converted/{nb_dir_relpath}/solutions/{nb_name}",
        )

        would create the following output structure:

        C:/converted
        ├── lectures
        │   ├── week1
        │   │   ├── lecture1.ipynb
        │   │   ├── lecture1.ipynb
        │   │   └── solutions
        │   │       └── lecture1.ipynb
        │   │       └── lecture2.ipynb
        │   └── week2
        │       ├── lecture3.ipynb
        │       ├── lecture4.ipynb
        │       └── solutions
        │           └── lecture3.ipynb
        │           └── lecture4.ipynb
        └── assignments
            ├── week1.ipynb
            ├── week2.ipynb
            └── solutions
                ├── week1.ipynb
                └── week2.ipynb

        To make specifying output paths even easier and to maintain backwards compatibility, the following shortcuts are provided:

        1. If `output` does not end with `.ipynb` and does not contain any placeholders, the provided path will be interpreted as a directory and the notebooks will be saved in `{output}/{nb_relpath}`, i.e. the following calls are equivalent:

           convert('mycourse', output = 'out')
           convert('mycourse', output = 'out/{nb_relpath}')

        2. If `solution` does not end with `.ipynb` and does not contain any placeholders, the provided path will be interpreted as a directory and the notebooks will be saved in `{solution}/{nb_dir_relpath}/{nb_basename}-solution.{nb_ext}`, i.e. the following calls are equivalent:

            convert('mycourse', solution = 'out')
            convert('mycourse', solution = 'out/{nb_dir_relpath}/{nb_basename}-solution.{nb_ext}')
    """
    log.log(f"Converting notebooks in {input} to {output}")
    input_folder = os.path.dirname(input) if os.path.isfile(input) else input

    if os.path.isfile(input):
        input_paths = [input]
    elif os.path.isdir(input):
        input_paths = []
        for root, dirs, files in os.walk(input, topdown=True):
            dirs[:] = [d for d in dirs if not d[0] == "."]
            for file in files:
                if file.lower().endswith(".ipynb"):
                    input_paths.append(os.path.join(root, file))
    else:
        log.warn(f"Input path {input} does not exist")
        return
    if len(input_paths) == 0:
        log.warn(f"No notebooks found in {input}")
        return

    output_paths = []
    solution_paths = []
    for input_path in input_paths:

        output_path = None # CONTINUE HERE

        # Print status
    for ip, op, sp in zip(input_paths, output_paths, solution_paths):
        _convert_nb(ip, op, sp, force, dry_run)


def _convert_nb(input: Union[str, Path],
                output: Optional(Union[str, Path]) = None,
                solution: Optional(Union[str, Path]) = None,
                force: bool = False,
                dryrun: bool = False) -> None:
    """Convert a single notebook to its student version with and/or without solutions removed.

    Args:
        input: Path of input notebook.
        output: Path for storing the student notebook without solutions. If the parent directory does not exist, it will be created. If output is None, the conversion will be skipped.
        solution: Path for storing the student notebook with solutions. If the parent directory does not exist, it will be created. If solution is None, the conversion will be skipped.
        force: Overwrite existing output files without asking?
        dryrun: Skip writing to disk after performing conversions? Useful for testing without file changes.

    Examples:
        # Create student version with solutions removed/kept from dummy.ipynb
        _convert_nb("dummy.ipynb", output="dummy-converted.ipynb")
        _convert_nb("dummy.ipynb", solution="dummy-solution.ipynb")

        # Same as above but in one line
        _convert_nb("dummy.ipynb", output="dummy-converted.ipynb", solution="dummy-solution.ipynb")

        # Absolute paths work as well
        _convert_nb("C:/Users/max/dummy.ipynb", solution="C:/Users/max/dummy-solution.ipynb")

        # Overwrite existing files without asking
        _convert_nb("dummy.ipynb", output="dummy-converted.ipynb", force=True)

        # Don't write converted files to disk
        _convert_nb("dummy.ipynb", output="dummy-converted.ipynb", dryrun=True)
    """
    in_path = Path(input)
    out_path = Path(output) if output else None
    sol_path = Path(solution) if solution else None
    if out_path or sol_path:
        log.log(f"Reading {in_path}")
        in_text = nbformat.read(in_path, as_version=4)
        resources = {"path": in_path}
    if out_path:
        out_config = traitlets.config.Config()
        out_config.NotebookExporter.preprocessors = [Linter, AddTags, RemoveSolutions, ClearOutputPreprocessor]
        out_converter = NotebookExporter(out_config)
        log.log(f"Converting {in_path} to student version without solutions")
        out_text = out_converter.from_notebook_node(in_text, resources)[0]
        if not dryrun:
            write(text = out_text, path = out_path, force = force)
    if sol_path:
        sol_config = traitlets.config.Config()
        sol_config.NotebookExporter.preprocessors = [AddTags, ClearOutputPreprocessor]
        sol_converter = NotebookExporter(sol_config)
        log.log(f"Converting {in_path} to student with solutions")
        sol_text = sol_converter.from_notebook_node(in_text, resources)[0]
        if not dryrun:
            write(text = sol_text, path = sol_path, force = force)


def write(text: str, path: str, force: bool = False) -> None:
    """
    Write text to path.
    If the parent directory does not exist, it will be created.
    If the path exists already and force is False, the user will be asked if they want to overwrite the file.
    If stdout is not a tty, a warning message will be printed instead.
    If force is True, the file will be overwritten without asking.

    Args:
        text: The text to write.
        path: The path of the file to write to. If the parent directory does not exist, it will be created.
        force: Overwrite existing files without asking?
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or force:
        log.log(f"Writing {path}.")
        with open(path, "w", newline="\n") as f:
            f.write(text)
        return
    if not sys.stdout.isatty():
        log.log(f"Skipped writing {path} because it exists already and force is False.")
        return
    overwrite = ''
    while overwrite.lower() not in ['y', 'n']:
        overwrite = input(f"File {path} exists. Overwrite? (y/n): ")
    if overwrite.lower() == 'y':
        with open(path, "w", newline="\n") as f:
            f.write(text)
