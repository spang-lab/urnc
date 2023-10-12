from nbconvert.preprocessors.base import Preprocessor

import re
import urnc.preprocessor.util as util
from urnc.preprocessor.util import Keywords, Tags
import urnc.logger as log


def end_assignment(assignment_id, has_solution):
    if assignment_id is None:
        return
    if not has_solution:
        log.warn(f"Assignment {assignment_id} has no solution")


class AddTags(Preprocessor):
    def preprocess(self, notebook, resources):
        assignment_ids = set()
        assignment_id = None
        has_solution = False

        for cell in notebook.cells:
            if re.match(Keywords.ASSIGNMENT_DEPRECATED, cell.source, re.IGNORECASE):
                log.warn(
                    "'Exercise' as Keyword is deprecated. Use 'Assignment' instead")
            if match := re.search(Keywords.ASSIGNMENT_START, cell.source, re.IGNORECASE):
                end_assignment(assignment_id, has_solution)
                has_solution = False
                assignment_id = match.group(1)
                util.set_tag(cell, Tags.ASSIGNMENT_START)
                if assignment_id in assignment_ids:
                    log.error("Duplicate Assignment id '%s'" % assignment_id)
                else:
                    assignment_ids.add(assignment_id)
                log.dbg("Detected Assignment '%s'" % assignment_id)
            elif util.has_header(cell) and assignment_id is not None:
                end_assignment(assignment_id, has_solution)
                assignment_id = None
            if assignment_id is None:
                continue
            util.set_tag(cell, Tags.ASSIGNMENT)
            cell.metadata.assignment_id = assignment_id

            if re.search(Keywords.SOLUTION, cell.source, re.IGNORECASE) or util.has_tag(
                cell, Tags.SOLUTION
            ):
                log.dbg(" Detected Solution cell %s" %
                        util.cell_preview(cell))
                util.set_tag(cell, Tags.SOLUTION)
                has_solution = True
        end_assignment(assignment_id, has_solution)
        return notebook, resources
