from nbconvert.preprocessors.base import Preprocessor


class ClearOutputs(Preprocessor):
    """
    Removes the output from all code cells in a notebook.
    """

    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
        return cell, resources
