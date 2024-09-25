from nbconvert.preprocessors.base import Preprocessor

import re
import urnc.preprocessor.util as util
from urnc.preprocessor.util import Keywords, Tags
import urnc.logger as log


def is_assignment_start(cell):
    if util.has_tag(cell, Tags.NORMAL):
        return None
    opts = re.IGNORECASE | re.MULTILINE
    if match := re.search(Keywords.ASSIGNMENT_DEPRECATED, cell.source, opts):
        id = util.to_snake_case(match.group(1))
        return id
    if match := re.search(Keywords.ASSIGNMENT_START, cell.source, opts):
        id = util.to_snake_case(match.group(1))
        return id
    return None


def is_solution(cell):
    if util.has_tag(cell, Tags.NORMAL):
        return False
    if util.has_tag(cell, Tags.SOLUTION):
        return True
    opts = re.IGNORECASE | re.MULTILINE
    return re.search(Keywords.SOLUTION, cell.source, opts)


def is_assignment_end(cell, assignment_id):
    if util.has_tag(cell, Tags.NORMAL):
        return False
    if assignment_id is None:
        return False
    if cell.cell_type != "markdown":
        return False
    if is_solution(cell):
        return False
    if re.search(Keywords.HEADER, cell.source, re.MULTILINE):
        return True
    return False


class AddTags(Preprocessor):
    def preprocess(self, nb, resources):
        assignment_ids = set()
        assignment_id = None
        has_solution = False

        for cell in nb.cells:
            if is_assignment_end(cell, assignment_id):
                if not has_solution:
                    log.warn(f"Assignment {assignment_id} has no solution")
                assignment_id = None

            if id := is_assignment_start(cell):
                assignment_id = id
                has_solution = False
                util.set_tag(cell, Tags.ASSIGNMENT_START)
                if assignment_id in assignment_ids:
                    log.warn("Duplicate Assignment id '%s'" % assignment_id)
                else:
                    assignment_ids.add(assignment_id)
                log.dbg("Detected Assignment '%s'" % assignment_id)

            if assignment_id:  # check if cell is part of the assignment
                util.set_tag(cell, Tags.ASSIGNMENT)
                cell.metadata.assignment_id = assignment_id

            if is_solution(cell):
                preview = util.cell_preview(cell)
                if assignment_id is None:
                    log.dbg(f"Solution cell is not part of an assignment: {preview}")
                log.dbg(f"Detected Solution cell {preview}")
                util.set_tag(cell, Tags.SOLUTION)
                has_solution = True

        if assignment_id is not None and not has_solution:
            log.warn(f"Assignment {assignment_id} has no solution")

        return nb, resources
