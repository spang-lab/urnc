"""Create student version of one or more Jupyter notebooks"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union, Tuple

import nbformat
import traitlets
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
            dry_run: bool = False,
            ask: bool = True) -> None:
    """Convert one or multiple notebooks to its student version with and/or without solutions removed.

    Args:
        input: The input path. Can be either the path to a single ipynb file or the path to a directory containing ipynb files.
        output: Path for storing the student notebooks with solutions removed. Directories will be created if necessary. If `output` is None, the conversion will be skipped. Supports placeholder variables. For details see section "Details" below.
        solution: Path for storing the student notebooks with solutions kept. Directories will be created if necessary. If `solution` is None, the conversion will be skipped. Supports placeholder variables. For details see section "Details" below.
        force: If true, existing output files will be overwritten.
        dry_run: If true, input files will be converted but not written to disk. This is useful for checking if the conversion works without changing any files.
        ask: Should the user be asked if existing files should be overwritten?

    Details:
        A call like `convert("C:/Users/max/mycourse", ...)` will search `C:/Users/max/mycourse` recursively for notebooks and convert each notebook to student versions. To be able to specify output paths in a simple yet flexible way, the following placeholder variables are provided: nb.abspath, nb.absdirpath, nb.rootpath, nb.relpath, nb.reldirpath, nb.name, nb.basename and nb.ext. To understand the meaning of each placeholder mean, consider the following folder structure:

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

        The above course contains the following six notebooks, lecture1.ipynb, lecture2.ipynb, lecture3.ipynb, lecture4.ipynb, week1.ipynb and week2.ipynb. The following table shows the value of each placeholder variable exemplarily for notebook C:/Users/max/mycourse/lectures/week2/lecture1.ipynb:

        | nb.abspath    | C:/Users/max/mycourse/lectures/week2/lecture1.ipynb |
        | nb.absdirpath | C:/Users/max/mycourse/lectures/week2                |
        | nb.rootpath   | C:/Users/max/mycourse                               |
        | nb.relpath    |                       lectures/week2/lecture1.ipynb |
        | nb.reldirpath |                       lectures/week2/               |
        | nb.name       |                                      lecture1.ipynb |
        | nb.basename   |                                      lecture1       |
        | nb.ext        |                                               ipynb |

        I.e. the following function call

        convert(
            input = "C:/Users/max/mycourse",
            output = "C:/converted/{nb.relpath}",
            solution = "C:/converted/{nb.reldirpath}/solutions/{nb.name}",
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

        To make specifying output paths less verbose and to maintain backwards compatibility, the following shortcuts are provided:

        1. If `output` does not end with `.ipynb` and does not contain any placeholders, the provided path will be interpreted as a directory and the notebooks will be saved in `{output}/{nb.relpath}`, i.e. the following calls are equivalent:

           convert('mycourse', output = 'out')
           convert('mycourse', output = 'out/{nb.relpath}')

        2. If `solution` does not end with `.ipynb` and does not contain any placeholders, the provided path will be interpreted as a directory and the notebooks will be saved in `{solution}/{nb.reldirpath}/{nb.basename}-solution.{nb.ext}`, i.e. the following calls are equivalent:

            convert('mycourse', solution = 'out')
            convert('mycourse', solution = 'out/{nb.reldirpath}/{nb.basename}-solution.{nb.ext}')

    Examples:
        convert("/path/to/single_notebook.ipynb", "/path/to/output", dry_run=True)
        convert("/path/to/notebooks", "/path/to/output", force=True)
    """
    log.log(f"Converting notebooks in {input}")
    nbs = get_nb_paths(input)
    if output and (not "{" in output) and (not output.lower().endswith(".ipynb")):
        output = f"{output}/{{nb.relpath}}"
    if solution and (not "{" in solution) and (not solution.lower().endswith(".ipynb")):
        solution = f"{solution}/{{nb.reldirpath}}/{{nb.basename}}-solution.{{nb.ext}}"
    for nb in nbs:
        convert_nb(input=nb, force=force, dry_run=dry_run, ask=ask,
                   output=output.format(nb=nb) if output else None,
                   solution=solution.format(nb=nb) if solution else None)


class NbPath(type(Path())):
    # By subclassing `type(Path())` instead of `Path` we subclass `WindowsPath` on Windows and `PosixPath` on Linux/MacOS. This is necessary because instances of the base class `Path` require some properties (e.g. `_flavour`) which are only set by the constructors of the respective subclasses. For details see <https://stackoverflow.com/questions/29850801/subclass-pathlib-path-fails>.

    def __new__(cls, abspath: str, rootpath: str):
        """Path to a jupyter notebook inside a arbitrarily nested directory structure.

        Attributes:
            abspath: Absolute path to the notebook.
            absdirpath: Absolute path to the directory containing the notebook.
            rootpath: Absolute path to the root directory of the notebook.
            relpath: Relative path to the notebook from the root directory.
            reldirpath: Relative path to the directory containing the notebook from the root directory.
            name: Name of the notebook including extension.
            basename: Name of the notebook without extension.
            ext: Extension of the notebook without the dot.

        Example:
            abspath = "C:/Users/max/mycourse/lectures/week2/lecture1.ipynb"
            rootpath = "C:/Users/max/mycourse"
            nb = NbPath(abspath, rootpath)
            nb.abspath    == "C:/Users/max/mycourse/lectures/week2/lecture1.ipynb"
            nb.absdirpath == "C:/Users/max/mycourse/lectures/week2"
            nb.rootpath   == "C:/Users/max/mycourse"
            nb.relpath    == "lectures/week2/lecture1.ipynb"
            nb.reldirpath == "lectures/week2"
            nb.name       == "lecture1.ipynb"
            nb.basename   == "lecture1"
            nb.ext        == "ipynb"
        """
        self = super().__new__(cls, abspath)
        self.rootpath = Path(rootpath)
        assert self.exists(), f"Notebook {self} does not exist"
        assert self.rootpath.exists(), f"Directory {self.rootpath} does not exist"
        self.abspath = self.absolute()
        self.absdirpath = self.parent.absolute()
        self.relpath = self.relative_to(self.rootpath)
        self.reldirpath = self.absdirpath.relative_to(self.rootpath)
        self.basename = self.stem
        self.ext = self.suffix[1:] if self.suffix.startswith(".") else self.suffix
        return self


def get_nb_paths(input: str) -> List[NbPath]:
    """Creates `NbPath` objects from all notebook files in input and returns them as list."""
    input = Path(os.path.abspath(input))
    nbs = []
    if input.is_file():
        nb = NbPath(abspath=input, rootpath=input.parent)
        nbs.append(nb)
    elif input.is_dir():
        for root, dirs, files in os.walk(input, topdown=True):
            dirs[:] = [d for d in dirs if not d[0] == "."]
            files[:] = [f for f in files if f.lower().endswith(".ipynb")]
            for file in files:
                nb = NbPath(abspath=os.path.join(root, file), rootpath=input)
                nbs.append(nb)
    else:
        log.warn(f"Input path {input} does not exist")
    return nbs


def convert_nb(input: Union[str, Path],
               output: Optional[Union[str, Path]] = None,
               solution: Optional[Union[str, Path]] = None,
               force: bool = False,
               dry_run: bool = False,
               ask: bool = True) -> None:
    """Convert a single notebook to its student version with and/or without solutions removed.

    Args:
        input: Path of input notebook.
        output: Path for storing the student notebook without solutions. If the parent directory does not exist, it will be created. If output is None, the conversion will be skipped.
        solution: Path for storing the student notebook with solutions. If the parent directory does not exist, it will be created. If solution is None, the conversion will be skipped.
        force: Overwrite existing output files without asking?
        dry_run: Skip writing to disk after performing conversions? Useful for testing without file changes.
        ask: Should the user be asked if existing files should be overwritten?

    Examples:
        # Create student version with solutions removed/kept from dummy.ipynb
        convert_nb("dummy.ipynb", output="dummy-converted.ipynb")
        convert_nb("dummy.ipynb", solution="dummy-solution.ipynb")

        # Same as above but in one line
        convert_nb("dummy.ipynb", output="dummy-converted.ipynb", solution="dummy-solution.ipynb")

        # Absolute paths work as well
        convert_nb("C:/Users/max/dummy.ipynb", solution="C:/Users/max/dummy-solution.ipynb")

        # Overwrite existing files without asking
        convert_nb("dummy.ipynb", output="dummy-converted.ipynb", force=True)

        # Don't write converted files to disk
        convert_nb("dummy.ipynb", output="dummy-converted.ipynb", dry_run=True)
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
        if not dry_run:
            write(text=out_text, path=out_path, force=force, ask=ask)
    if sol_path:
        sol_config = traitlets.config.Config()
        sol_config.NotebookExporter.preprocessors = [AddTags, ClearOutputPreprocessor]
        sol_converter = NotebookExporter(sol_config)
        log.log(f"Converting {in_path} to student with solutions")
        sol_text = sol_converter.from_notebook_node(in_text, resources)[0]
        if not dry_run:
            write(text=sol_text, path=sol_path, force=force, ask=ask)


def write(text: str, path: str, force: bool = False, ask=True) -> None:
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
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or force:
        log.log(f"Writing {path}.")
        with open(path, "w", newline="\n") as f:
            f.write(text)
        return
    if not sys.stdout.isatty() or not ask:
        log.log(f"Skipped writing {path} because it exists already and force is False.")
        return
    overwrite = ''
    while overwrite.lower() not in ['y', 'n']:
        overwrite = input(f"File {path} exists. Overwrite? (y/n): ")
    if overwrite.lower() == 'y':
        with open(path, "w", newline="\n") as f:
            f.write(text)
