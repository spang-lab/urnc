import urnc
import nbformat

def test_convert():
    # Init course containing solution cells
    urnc.init.init(name="Test Course", path="test_course")
    with open('test_course/example.ipynb', encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    num_solution_cells = sum('## Solution' in (cell.source or '') for cell in nb.cells)
    assert num_solution_cells > 0

    # Convert course to student version and check that solution cells are removed
    config = urnc.config.default_config("test_course")
    config["convert"]["write_mode"] = "overwrite"
    input = 'test_course/example.ipynb'
    targets = [{"type": "student", "path": "{nb.abspath}"}]
    urnc.convert.convert(config, input, targets)
    with open('test_course/example.ipynb', encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    num_solution_cells = sum('## Solution' in (cell.source or '') for cell in nb.cells)
    assert num_solution_cells == 0
