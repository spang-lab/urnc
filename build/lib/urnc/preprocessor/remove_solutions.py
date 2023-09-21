from nbconvert.preprocessors.base import Preprocessor

import urnc.preprocessor.util as util
from urnc.preprocessor.util import Tags, Keywords
import re


def process_comments(cell):
    text = cell.source
    lines = text.split("\n")
    last_tag = None
    found_tag = False
    tlines = []
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
        tlines.append((line, last_tag))
    if not found_tag:
        return None
    slines = []
    for line, tag in tlines:
        if tag is None:
            slines.append(line)
        if tag == Tags.SOLUTION:
            continue
        if tag == Tags.SKELETON:
            uncom = re.sub(r"^#\s?", "", line)
            slines.append(uncom)
    if len(slines) == 0:
        return None
    cell.source = "\n".join(slines)
    return cell


class RemoveSolutions(Preprocessor):
    def preprocess(self, notebook, resources):
        cells = []
        for cell in notebook.cells:
            if util.has_tag(cell, Tags.SOLUTION):
                cell = process_comments(cell)
            if cell is not None:
                cells.append(cell)
        notebook.cells = cells
        return notebook, resources
