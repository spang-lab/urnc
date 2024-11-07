from nbconvert.preprocessors.base import Preprocessor
from traitlets.config import List

from urnc.preprocessor.util import has_tag


class ClearTaggedCells(Preprocessor):
    tags = List([], help="List of tags to clear from the notebook").tag(config=True)

    def preprocess(self, nb, resources):
        cells = []
        for cell in nb.cells:
            if any(has_tag(cell, tag) for tag in self.tags):
                continue
            cells.append(cell)
        nb.cells = cells
        return nb, resources
