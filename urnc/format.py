from pathlib import Path
from typing import Optional


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
        self.rootpath = rootpath
        self.abspath = path.absolute()
        self.relpath = path.relative_to(rootpath)
        self.absdirpath = path.parent.absolute()
        self.reldirpath = self.absdirpath.relative_to(self.rootpath)
        self.name = path.name
        self.basename = path.stem
        self.ext = path.suffix[1:] if path.suffix.startswith(".") else path.suffix


def is_directory_path(pattern: Optional[str]) -> bool:
    if pattern is None:
        return False
    return "{" not in pattern and not pattern.endswith(".ipynb")


def format_path(path: Path, pattern: Optional[str], root: Path) -> Optional[Path]:
    if pattern is None:
        return None
    nbpath = NbPath(path, root)
    if is_directory_path(pattern):
        pattern = f"{pattern}/{{nb.relpath}}"

    return Path(pattern.format(nb=nbpath))
