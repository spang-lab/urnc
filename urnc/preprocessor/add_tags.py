from nbconvert.preprocessors.base import Preprocessor

import re
import urnc.preprocessor.util as util
from urnc.preprocessor.util import Keywords, Tags


def critical_error(text):
    RED = "\033[1;31m"
    RESET = "\033[0;0m"
    print("%sCritical Error: %s %s" % (RED, text, RESET))


def end_exercise(exercise_id, has_solution):
    if exercise_id is None:
        return
    if not has_solution:
        critical_error("Exercise '%s' has no solution" % exercise_id)


class AddTags(Preprocessor):
    def preprocess(self, notebook, resources):
        verbose = resources["verbose"]

        exercise_ids = set()
        exercise_id = None
        has_solution = False

        for cell in notebook.cells:
            if match := re.search(Keywords.EXERCISE_START, cell.source, re.IGNORECASE):
                end_exercise(exercise_id, has_solution)
                has_solution = False
                exercise_id = match.group(1)
                util.set_tag(cell, Tags.EXERCISE_START)
                if exercise_id in exercise_ids:
                    critical_error("Duplicate Exercise id '%s'" % exercise_id)
                else:
                    exercise_ids.add(exercise_id)
                if verbose:
                    print("Detected Exercise '%s'" % exercise_id)
            elif util.has_header(cell) and exercise_id is not None:
                end_exercise(exercise_id, has_solution)
                exercise_id = None
            if exercise_id is None:
                continue
            util.set_tag(cell, Tags.EXERCISE)
            cell.metadata.exercise_id = exercise_id

            if re.search(Keywords.SOLUTION, cell.source, re.IGNORECASE) or util.has_tag(
                cell, Tags.SOLUTION
            ):
                if verbose:
                    print(" Detected Solution cell %s" % util.cell_preview(cell))
                util.set_tag(cell, Tags.SOLUTION)
                has_solution = True
        end_exercise(exercise_id, has_solution)
        return notebook, resources
