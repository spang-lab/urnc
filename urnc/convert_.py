"""Create student version of one or more Jupyter notebooks"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union

import nbformat
from traitlets.config import Config
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.writers import FilesWriter
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor

import urnc
from urnc.format import format_path
import urnc.logger as log
from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.lint import Linter
from urnc.preprocessor.solutions import SolutionRemover, SkeletonRemover


student_preprocessors = [Linter, AddTags, SolutionRemover, ClearOutputPreprocessor]
student_config = config.Config()
student_config.ClearOutputPreprocessor.remove_metadata_fields = {"collapsed"}
student_config.NotebookExporter.preprocessors = student_preprocessors
student_converter = NotebookExporter(student_config)

solution_preprocessors = [AddTags, SkeletonRemover, ClearOutputPreprocessor]
solution_config = config.Config()
solution_config.NotebookExporter.preprocessors = solution_preprocessors
solution_converter = NotebookExporter(solution_config)


def convert(
    input: Path = Path("."),
    output: Optional[str] = None,
    solution: Optional[str] = None,
    config: dict = None,
) -> None:
    """Convert one or multiple notebooks to its student version with and/or without solutions removed.

    Args:
        input: The input path. Can be either the path to a single ipynb file or the path to a directory containing ipynb files.
        output: Path for storing the student notebooks with solutions removed. Directories will be created if necessary. If ``output`` is None, the conversion will be skipped. Supports placeholder variables. For details see section "Details" below.
        solution: Path for storing the student notebooks with solutions kept. Directories will be created if necessary. If ``solution`` is None, the conversion will be skipped. Supports placeholder variables. For details see section "Details" below.
        force: If true, existing output files will be overwritten.
        dry_run: If true, input files will be converted but not written to disk. This is useful for checking if the conversion works without changing any files.
        ask: Should the user be asked if existing files should be overwritten?

    Details:
        A call like ``convert("C:/Users/max/mycourse", ...)`` will search ``C:/Users/max/mycourse`` recursively for notebooks and convert each notebook to student versions. To be able to specify output paths in a simple yet flexible way, the following placeholder variables are provided: ``nb.abspath``, ``nb.absdirpath``, ``nb.rootpath``, ``nb.relpath``, ``nb.reldirpath``, ``nb.name``, ``nb.basename`` and ``nb.ext``. To understand the meaning of each placeholder mean, consider the following folder structure::

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

        The above course contains the following six notebooks: ``lecture1.ipynb``, ``lecture2.ipynb``, ``lecture3.ipynb``, ``lecture4.ipynb``, ``week1.ipynb`` and ``week2.ipynb``. The following table shows the value of each placeholder variable exemplarily for notebook ``C:/Users/max/mycourse/lectures/week2/lecture1.ipynb``::

            | nb.abspath    | C:/Users/max/mycourse/lectures/week2/lecture1.ipynb |
            | nb.absdirpath | C:/Users/max/mycourse/lectures/week2                |
            | nb.rootpath   | C:/Users/max/mycourse                               |
            | nb.relpath    |                       lectures/week2/lecture1.ipynb |
            | nb.reldirpath |                       lectures/week2/               |
            | nb.name       |                                      lecture1.ipynb |
            | nb.basename   |                                      lecture1       |
            | nb.ext        |                                               ipynb |

        I.e. the following function call:

            >>> convert(
            >>>     input = "C:/Users/max/mycourse",
            >>>     output = "C:/converted/{nb.relpath}",
            >>>     solution = "C:/converted/{nb.reldirpath}/solutions/{nb.name}",
            >>> )

        would create the following output structure::

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

        To make specifying output paths less verbose and to maintain backwards compatibility, the following shortcuts are provided:

        1. If ``output`` does not end with ``.ipynb`` and does not contain any placeholders, the provided path will be interpreted as a directory and the notebooks will be saved in ``{output}/{nb.relpath}``, i.e. the following calls are equivalent::

            convert('mycourse', output = 'out')
            convert('mycourse', output = 'out/{nb.relpath}')

        2. If ``solution`` does not end with ``.ipynb`` and does not contain any placeholders, the provided path will be interpreted as a directory and the notebooks will be saved in ``{solution}/{nb.reldirpath}/{nb.basename}-solution.{nb.ext}``, i.e. the following calls are equivalent::

                convert('mycourse', solution = 'out')
                convert('mycourse', solution = 'out/{nb.reldirpath}/{nb.basename}-solution.{nb.ext}')

    Examples:
        >>> convert("/path/to/single_notebook.ipynb", "/path/to/output", dry_run=True)
        >>> convert("/path/to/notebooks", "/path/to/output", force=True)
    """
    nbconfig = Config(config)

    if input.is_file():
        out_path = format_path(input, output, input.parent)
        sol_path = format_path(input, solution, input.parent)

    log.log(f"Converting notebooks in {os.path.abspath(input)}")
    nbs = get_nb_paths(input)
    outstr = str(output).lower() if output else "{}"
    solstr = str(solution).lower() if solution else "{}"
    if "{" not in outstr and not outstr.endswith(".ipynb"):
        output = f"{output}/{{nb.relpath}}"
    if not ("{" in solstr or solstr.endswith(".ipynb")):
        solution = f"{solution}/{{nb.reldirpath}}/{{nb.basename}}-solution.{{nb.ext}}"

    for nb in nbs:
        inb = nb.abspath
        onb = Path(str(output).format(nb=nb)) if output else None
        snb = Path(str(solution).format(nb=nb)) if solution else None
        convert_nb(
            input=inb, output=onb, solution=snb, force=force, dry_run=dry_run, ask=ask
        )


def convert_nb(
    source: Path,
    target: Optional[Path] = None,
    target_type: str = "student",
    force: bool = False,
    ask: bool = True,
) -> None:
    converter = None
    if target_type == "student":
        student_preprocessors = [
            Linter,
            AddTags,
            SolutionRemover,
            ClearOutputPreprocessor,
        ]
        student_config = config.Config()
        student_config.NotebookExporter.preprocessors = student_preprocessors
        student_converter = NotebookExporter(student_config)


def convert_nb(
    input: Union[str, Path],
    output: Optional[Union[str, Path]] = None,
    solution: Optional[Union[str, Path]] = None,
    force: bool = False,
    dry_run: bool = False,
    ask: bool = True,
) -> None:
    """Convert a single notebook to its student version with and/or without solutions removed.

    Args:
        input: Path of input notebook.
        output: Path for storing the student notebook without solutions. If the parent directory does not exist, it will be created. If output is None, the conversion will be skipped.
        solution: Path for storing the student notebook with solutions. If the parent directory does not exist, it will be created. If solution is None, the conversion will be skipped.
        force: Overwrite existing output files without asking?
        dry_run: Skip writing to disk after performing conversions? Useful for testing without file changes.
        ask: Should the user be asked if existing files should be overwritten?

    Examples:
        >>> # Create student version with solutions removed/kept from dummy.ipynb
        >>> convert_nb("dummy.ipynb", output="dummy-converted.ipynb")
        >>> convert_nb("dummy.ipynb", solution="dummy-solution.ipynb")
        >>>
        >>> # Same as above but in one line
        >>> convert_nb("dummy.ipynb", output="dummy-converted.ipynb", solution="dummy-solution.ipynb")
        >>>
        >>> # Absolute paths work as well
        >>> convert_nb("C:/Users/max/dummy.ipynb", solution="C:/Users/max/dummy-solution.ipynb")
        >>>
        >>> # Overwrite existing files without asking
        >>> convert_nb("dummy.ipynb", output="dummy-converted.ipynb", force=True)
        >>>
        >>> # Don't write converted files to disk
        >>> convert_nb("dummy.ipynb", output="dummy-converted.ipynb", dry_run=True)
    """
    cwd = os.getcwd()
    in_path = Path(input)
    in_relpath = in_path.relative_to(cwd) if in_path.is_relative_to(cwd) else in_path
    out_path = Path(output) if output else None
    sol_path = Path(solution) if solution else None
    log.log(f"Reading {in_relpath}")
    in_text = nbformat.read(in_path, as_version=4)
    resources = {"path": in_path}
    if out_path:
        log.log(f"Converting {in_relpath} to student version without solutions")
        out_text = student_converter.from_notebook_node(in_text, resources)[0]
        if not dry_run:
            write(text=out_text, path=out_path, force=force, ask=ask)
    if sol_path:
        log.log(f"Converting {in_relpath} to student version with solutions")
        sol_text = solution_converter.from_notebook_node(in_text, resources)[0]
        if not dry_run:
            write(text=sol_text, path=sol_path, force=force, ask=ask)


def get_nb_paths(input: Union[str, Path]) -> List[Path]:
    """Creates `NbPath` objects from all notebook files in input and returns them as list."""
    input = Path(os.path.abspath(input))
    nbs = []
    if input.is_file() and input.suffix == ".ipynb":
        nb = NbPath(path=input, rootpath=input.parent)
        nbs.append(nb)
    elif input.is_dir():
        for root, dirs, files in os.walk(input, topdown=True):
            dirs[:] = [d for d in dirs if not d[0] == "."]
            files[:] = [f for f in files if f.lower().endswith(".ipynb")]
            for file in files:
                nb = NbPath(path=os.path.join(root, file), rootpath=input)
                nbs.append(nb)
    else:
        log.warn(
            f"Input path {input} does not exist or does not contain any notebooks."
        )
    return nbs


def write(text: str, path: Union[str, Path], force: bool = False, ask=True) -> None:
    """
    Write text to path.
    If the parent directory does not exist, it will be created.
    If the path exists already and force is False, the user will be asked if they want to overwrite the file.
    If stdout is not a tty or ask is False, a warning message will be printed instead.
    If force is True, the file will be overwritten without asking.

    Args:
        text: The text to write.
        path: The path of the file to write to. If the parent directory does not exist, it will be created.
        force: Overwrite existing files without asking?
        ask: Ask the user if they want to overwrite the file if it exists already and force is False?
    """
    writer = FilesWriter()

    cwd = os.getcwd()
    path = Path(path)
    relpath = path.relative_to(cwd) if path.is_relative_to(cwd) else path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or force:
        log.log(f"Writing {relpath}.")
        with open(path, "w", newline="\n") as f:
            f.write(text)
        return
    if not sys.stdout.isatty() or not ask:
        log.log(
            f"Skipped writing {relpath} because it exists already and force is False."
        )
        return
    overwrite = ""
    while overwrite.lower() not in ["y", "n"]:
        overwrite = input(f"File {path} exists. Overwrite? (y/n): ")
    if overwrite.lower() == "y":
        with open(path, "w", newline="\n") as f:
            f.write(text)
