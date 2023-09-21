import inspect
import re
from nbconvert.preprocessors.base import Preprocessor

import urnc.preprocessor.util as util


def replace_local_link(cell, verbose):
    if cell.cell_type != "markdown":
        return
    if not re.search(r"\(#Exercise-.*\)", cell.source, re.IGNORECASE):
        return
    if verbose:
        print("Detected Link to exercise.")
    cell.source = re.sub(r"#Exercise-", "#ex-", cell.source, re.IGNORECASE)


class ProcessExercises(Preprocessor):
    def preprocess(self, notebook, resources):
        verbose = resources["verbose"]
        for cell in notebook.cells:
            replace_local_link(cell, verbose)
            if util.has_tag(cell, util.Tags.EXERCISE_START):
                eid = cell.metadata.exercise_id
                html = """
                    <a class="anchor" name="ex-%s"></a>
                    <h3>   ✎    Exercise</h3>
                """ % (
                    eid
                )
                cell.source = inspect.cleandoc(html)
        return notebook, resources
