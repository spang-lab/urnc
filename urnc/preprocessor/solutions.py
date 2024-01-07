from typing import Tuple, Dict, Union
from nbconvert.preprocessors.base import Preprocessor

import urnc.preprocessor.util as util
from urnc.preprocessor.util import Tags, Keywords
import re

from nbformat.notebooknode import NotebookNode


def remove_solution_lines(cell: NotebookNode) -> Union[NotebookNode, None]:
    """
    Remove solution lines from a cell.

    This function takes a cell from a Jupyter Notebook as input, removes solution lines, uncomments skeleton lines and returns the cell.
    If no lines remain after removing the solutions, the function returns None (i.e. the whole cell is removed).
    If no Solution or Skeleton patterns are found in the cell, the function returns None as well.
    Solutions and Skeleton pattern are defined at `urnc.preprocessor.util.Keywords <https://spang-lab.github.io/urnc/urnc.preprocessor.html#urnc.preprocessor.util.Keywords>`_.

    Parameters:
        cell: The cell to process.

    Returns:
        Either the cell without solutions lines and uncommented skeleton lines or None.
    """
    text = cell.source
    lines = text.split("\n")
    last_tag = None
    found_tag = False
    tagged_lines = []
    for line in lines:
        if re.match(Keywords.SOLUTION, line, re.IGNORECASE):
            last_tag = Tags.SOLUTION
            found_tag = True
            continue
        if re.match(Keywords.SKELETON, line, re.IGNORECASE):
            last_tag = Tags.SKELETON
            found_tag = True
            continue
        if re.match(Keywords.SOLUTION_END, line, re.IGNORECASE):
            last_tag = None
            continue
        tagged_lines.append((line, last_tag))
    if not found_tag:
        return None
    skeleton_lines = []
    for line, tag in tagged_lines:
        if tag is None:
            skeleton_lines.append(line)
        if tag == Tags.SOLUTION:
            continue
        if tag == Tags.SKELETON:
            uncom = re.sub(r"^#\s?", "", line)
            skeleton_lines.append(uncom)
    if len(skeleton_lines) == 0:
        return None
    cell.source = "\n".join(skeleton_lines)
    return cell


def remove_skeleton_lines(text: str) -> str:
    """
    Remove skeleton lines from a string.

    Parameters:
        text: The text to process.

    Returns:
        Text without skeleton lines.

    Examples::
        remove_skeleton_lines("### Skeleton\n# # a == ?") == ""
        remove_skeleton_lines("### Skeleton\n# # a == ?\n###") == "###"
        remove_skeleton_lines("### Solution\na = 100\n### Skeleton\n# # a == ?\n###") == "### Solution\na = 100\n###"
    """
    lines = text.split("\n")
    keep = []
    inside_skeleton = False
    for line in lines:
        if re.match(Keywords.SKELETON, line, re.IGNORECASE):
            inside_skeleton = True
        elif re.match(Keywords.SOLUTION_END, line, re.IGNORECASE):
            inside_skeleton = False
            keep.append(line)
        elif not inside_skeleton:
            keep.append(line)
    return "\n".join(keep)


class SolutionRemover(Preprocessor):
    def preprocess(self,
                   notebook: NotebookNode,
                   resources: Union[Dict, None] = None) -> Tuple[NotebookNode, Union[NotebookNode, None]]:
        """
        Preprocess the notebook by removing solutions lines from solution cells and uncommenting skeleton lines within solution cells.

        This function takes a notebook and resources as input, removes the solution lines from notebook cells  and returns the notebook and resources.

        Parameters:
            notebook: The notebook to preprocess.
            resources: The resources associated with the notebook.

        Returns:
            The preprocessed notebook and the resources.
        """
        cells = []
        for cell in notebook.cells:
            if util.has_tag(cell, Tags.SOLUTION):
                cell = remove_solution_lines(cell)
            if cell is not None:
                cells.append(cell)
        notebook.cells = cells
        return notebook, resources


class SkeletonRemover(Preprocessor):
    def preprocess(self,
                   notebook: NotebookNode,
                   resources: Union[Dict, None] = None) -> Tuple[NotebookNode, Union[NotebookNode, None]]:
        """
        Preprocess the notebook by removing skeleton lines from solution cells.

        This function takes a notebook and resources as input, removes the solution lines from notebook cells  and returns the notebook and resources.

        Parameters:
            notebook: The notebook to preprocess.
            resources: The resources associated with the notebook.

        Returns:
            The preprocessed notebook and the resources.
        """
        for cell in notebook.cells:
            if util.has_tag(cell, Tags.SOLUTION):
                cell.source = remove_skeleton_lines(text = cell.source)
        return notebook, resources