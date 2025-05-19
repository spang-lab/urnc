from pathlib import Path
from typing import Optional, Union
from urnc.config import TargetType, target_suffix
from urnc.logger import critical


class NbPath(object):
    def __init__(self, path: Path, rootpath: Path):
        """Path to a jupyter notebook inside a arbitrarily nested directory structure.

        Attributes:
            path (Path): Path object initialized from the provided path.
            abspath (str): Absolute path to the notebook.
            absdirpath (str): Absolute path to the directory containing the notebook.
            rootpath (str): Absolute path to the root directory of the notebook.
            relpath (str): Relative path to the notebook from the root directory.
            reldirpath (str): Relative path to the directory containing the notebook from the root directory.
            name (str): Name of the notebook including extension.
            basename (str): Name of the notebook without extension.
            ext (str): Extension of the notebook without the dot.

        Example:
            >>> path = "C:/Users/max/mycourse/lectures/week2/lecture1.ipynb"
            >>> rootpath = "C:/Users/max/mycourse"
            >>> nb = NbPath(path, rootpath)
            >>> nb.abspath    == "C:/Users/max/mycourse/lectures/week2/lecture1.ipynb"
            >>> nb.absdirpath == "C:/Users/max/mycourse/lectures/week2"
            >>> nb.rootpath   == "C:/Users/max/mycourse"
            >>> nb.relpath    == "lectures/week2/lecture1.ipynb"
            >>> nb.reldirpath == "lectures/week2"
            >>> nb.name       == "lecture1.ipynb"
            >>> nb.basename   == "lecture1"
            >>> nb.ext        == "ipynb"
        """
        self.path = path
        self.rootpath = rootpath.absolute()
        self.abspath = path.absolute()
        self.relpath = self.abspath.relative_to(self.rootpath)
        self.absdirpath = path.parent.absolute()
        self.reldirpath = self.absdirpath.relative_to(self.rootpath)
        self.name = path.name
        self.basename = path.stem
        self.ext = path.suffix[1:] if path.suffix.startswith(".") else path.suffix


def is_directory_path(path: Union[str, Path, None]) -> bool:
    if path is None:
        return False
    path_str = str(path)
    return "{" not in path_str and not path_str.endswith(".ipynb")


def format_path(input: Path,
                output: Union[str, Path, None],
                root: Path,
                type: str = TargetType.STUDENT) -> Optional[Path]:
    """
    Substitute placeholders in outpath with the correct values derived from srcpath and root

    Args:
        input: path of the input notebook
        output: path of the outbook notebook incl. placeholders
        root: path of the course root directory
        type: type of conversion (e.g. student, solution, etc.)
    """
    if output is None:
        return None
    output = str(output)
    if is_directory_path(output):
        suffix = target_suffix.get(type, lambda: critical(f"Unknown target type '{type}'. Aborting."))
        output = f"{output}/{{nb.reldirpath}}/{{nb.basename}}{suffix}.{{nb.ext}}"
    nbpath = NbPath(input, root)
    return Path(output.format(nb=nbpath))
