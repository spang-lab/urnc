import typing as t
import click
from nbconvert.preprocessors.base import Preprocessor
from traitlets import List, Unicode

import urnc.preprocessor.util as util
import re
from enum import StrEnum
from nbformat.notebooknode import NotebookNode


class LineTags(StrEnum):
    SOLUTION_KEY = "solution_key"
    SOLUTION = "solution"
    SKELETON_KEY = "skeleton_key"
    SKELETON = "skeleton"
    END_KEY = "end_key"
    NONE = "none"


class SolutionProcessor(Preprocessor):
    solution_keywords = List(
        ["solution"], help="Keywords to search for in the notebook headers"
    ).tag(config=True)
    solution_tag = Unicode("solution", help="Tag to assign to solution cells").tag(
        config=True
    )
    skeleton_keywords = List(
        ["skeleton"], help="Keywords to search for in the cell source"
    ).tag(config=True)
    end_keywords = List(["end"], help="Keywords to search for in the cell source").tag(
        config=True
    )
    output = Unicode(
        "skeleton", help="Which lines to keep. Either 'skeleton', 'solution' of 'none'"
    ).tag(config=True)

    def tag_line(self, line: str) -> t.Tuple[str, str]:
        if match := re.match(r"\s*(#{1,6})\s*(.+)?", line):
            level = len(match.group(1))
            text = match.group(2)
            print(level, text)
            if level == 1:
                return LineTags.NONE, line
            if util.starts_with(text, self.solution_keywords):
                return LineTags.SOLUTION_KEY, line
            if util.starts_with(text, self.skeleton_keywords):
                return LineTags.SKELETON_KEY, line
            if util.starts_with(text, self.end_keywords):
                return LineTags.END_KEY, line
            if not text:
                return LineTags.END_KEY, line
            return LineTags.NONE, line
        return LineTags.NONE, line

    def scan_lines(self, text: str) -> t.List[t.Tuple[str, str]]:
        lines = text.split("\n")
        tagged_lines = [self.tag_line(line) for line in lines]
        current_tag = LineTags.NONE
        for i, line in enumerate(tagged_lines):
            tag, text = line
            if tag == LineTags.SOLUTION_KEY:
                current_tag = LineTags.SOLUTION
                continue
            if tag == LineTags.SKELETON_KEY:
                current_tag = LineTags.SKELETON
                continue
            if tag == LineTags.END_KEY:
                current_tag = LineTags.NONE
                continue
            tagged_lines[i] = (current_tag, text)
        return tagged_lines

    def strip_cell(self, cell: NotebookNode) -> t.Optional[NotebookNode]:
        tagged_lines = self.scan_lines(cell.source)
        if all(tag == LineTags.NONE for tag, _ in tagged_lines):
            if self.output == "solution":
                return cell
            return None
        lines = []
        for tag, line in tagged_lines:
            if self.output == "skeleton":
                if tag == LineTags.SOLUTION:
                    continue
                if tag == LineTags.SKELETON:
                    uncommented = re.sub(r"^#\s?", "", line)
                    lines.append(uncommented)
                    continue
                if tag == LineTags.NONE:
                    lines.append(line)
            if self.output == "solution":
                if tag == LineTags.SKELETON:
                    continue
                if tag == LineTags.SOLUTION or tag == LineTags.NONE:
                    lines.append(line)
            if self.output == "none" and tag == LineTags.NONE:
                lines.append(line)
        if len(lines) == 0:
            return None
        cell.source = "\n".join(lines)
        return cell

    def preprocess(
        self, nb: NotebookNode, resources: t.Union[t.Dict, None] = None
    ) -> t.Tuple[NotebookNode, t.Union[t.Dict, None]]:
        if self.output not in ["skeleton", "solution", "none"]:
            click.UsageError(
                f"solution.output must be one of 'skeleton', 'solution' or 'none', not {self.output}"
            )

        cells = []
        for cell in nb.cells:
            if util.has_tag(cell, self.solution_tag):
                cell = self.strip_cell(cell)
            if cell is not None:
                cells.append(cell)
        nb.cells = cells
        return nb, resources
