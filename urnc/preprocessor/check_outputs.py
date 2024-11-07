from nbconvert.preprocessors.base import Preprocessor
from traitlets import Integer

from urnc.logger import error, warn
from urnc.preprocessor import util


class CheckOutputs(Preprocessor):
    max_line_count = Integer(30, help="Maximum number of lines in a cell output").tag(
        config=True
    )

    def check_output(self, cell) -> bool:
        outputs = cell.get("outputs", [])
        for output in outputs:
            if output.output_type == "error":
                preview = util.cell_preview(cell)
                error(f"Error in cell {preview}: {output.ename}")
                return False
            text = output.get("text", None)
            metadata = cell.get("metadata", {})
            is_scrolled = metadata.get("scrolled", False)
            if text is not None:
                text = "".join(text)
                line_count = text.count("\n")
                if line_count > self.max_line_count and not is_scrolled:
                    preview = util.cell_preview(cell)
                    warn(
                        f"Cell {preview} has {line_count} lines in output, consider setting the 'scrolled' metadata field"
                    )
                    return False
        return True

    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == "code":
            self.check_output(cell)
        return cell, resources
