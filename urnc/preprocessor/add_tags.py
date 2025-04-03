from nbconvert.preprocessors.base import Preprocessor

import re

from nbformat import NotebookNode
from traitlets import List, Unicode
import typing as t
import urnc.preprocessor.util as util
from urnc.logger import warn, dbg


def header_to_id(header: str) -> str:
    return re.sub(r"\W+|^(?=\d)", "_", header.lower()).strip("_")


def extract_header(cell):
    opts = re.IGNORECASE | re.MULTILINE
    if match := re.match(r"^(#{1,6})\s*(.+)", cell.source, opts):
        level = len(match.group(1))
        title = match.group(2)
        return level, title, header_to_id(title)
    if match := re.match(r"<h([1-6]).*>((.+)(?:\n.+)*)<\/h\1>", cell.source, opts):
        level = int(match.group(1))
        title = match.group(2).strip()
        return level, title, header_to_id(title)
    return None, None, None


class AddTags(Preprocessor):
    assignment_keywords = List(
        ["assignment"], help="Keywords to search for in the notebook headers"
    ).tag(config=True)
    solution_keywords = List(
        ["solution"], help="Keywords to search for in the notebook headers"
    ).tag(config=True)

    assignment_tag = Unicode(
        "assignment", help="Tag to assign to assignment cells"
    ).tag(config=True)
    assignment_start_tag = Unicode(
        "assignment-start", help="Tag to assign to the first cell of an assignment"
    ).tag(config=True)
    solution_tag = Unicode("solution", help="Tag to assign to solution cells").tag(
        config=True
    )
    ignore_tag = Unicode(
        "normal", help="Tag to assign to cells that should be ignored"
    ).tag(config=True)

    def is_assignment_start(self, cell: NotebookNode, header: t.Optional[str]) -> bool:
        if util.has_tag(cell, self.ignore_tag):
            return False
        return util.starts_with(header, self.assignment_keywords)

    def is_solution(self, cell: NotebookNode, header: t.Optional[str]) -> bool:
        if util.has_tag(cell, self.ignore_tag):
            return False
        if util.has_tag(cell, self.solution_tag):
            return True
        return util.starts_with(header, self.solution_keywords)

    def is_assignment_end(self, cell: NotebookNode, header: t.Optional[str]) -> bool:
        if util.has_tag(cell, self.ignore_tag):
            return False
        if not header:
            return False
        if cell.cell_type != "markdown":
            return False
        if self.is_solution(cell, header):
            return False
        return True

    def preprocess(self, nb, resources):
        assignment_ids = set()
        assignment_id = None
        has_solution = False

        for cell in nb.cells:
            _, header, id = extract_header(cell)

            if assignment_id and self.is_assignment_end(cell, header):
                if not has_solution:
                    warn(f"Assignment {assignment_id} has no solution")
                assignment_id = None

            if self.is_assignment_start(cell, header):
                assignment_id = id
                has_solution = False
                util.set_tag(cell, self.assignment_start_tag)
                if assignment_id in assignment_ids:
                    warn("Duplicate Assignment id '%s'" % assignment_id)
                else:
                    assignment_ids.add(assignment_id)
                dbg("Detected Assignment '%s'" % assignment_id)

            if assignment_id:  # check if cell is part of the assignment
                util.set_tag(cell, self.assignment_tag)
                cell.metadata.assignment_id = assignment_id

            if self.is_solution(cell, header):
                preview = util.cell_preview(cell)
                if assignment_id is None:
                    dbg(f"Solution cell is not part of an assignment: {preview}")
                dbg(f"Detected Solution cell {preview}")
                util.set_tag(cell, self.solution_tag)
                has_solution = True

        if assignment_id is not None and not has_solution:
            warn(f"Assignment {assignment_id} has no solution")

        return nb, resources
