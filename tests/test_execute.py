import nbformat
from traitlets.config import Config
from urnc.preprocessor.executor import ExecutePreprocessor
from urnc.preprocessor.clear_tagged import ClearTaggedCells
from urnc.preprocessor.check_outputs import CheckOutputs


def test_execute_notebook():
    nb = nbformat.v4.new_notebook(
        metadata={
            "papermill": {},
        },
        cells=[
            nbformat.v4.new_code_cell("print('Hello, world!')"),
        ],
    )
    executor = ExecutePreprocessor()
    ex_nb = executor.execute_notebook(nb)
    assert ex_nb.cells[0].outputs[0]["text"] == "Hello, world!\n"


def test_execute_error():
    nb = nbformat.v4.new_notebook(
        metadata={
            "papermill": {},
        },
        cells=[
            nbformat.v4.new_code_cell("print('Hello, world!'"),
        ],
    )
    executor = ExecutePreprocessor()
    ex_nb = executor.execute_notebook(nb)

    assert ex_nb.cells[0].outputs[0]["output_type"] == "error"


def test_pipeline():
    config = Config()
    config.ClearTaggedCells.tags = ["no-execute"]
    clearer = ClearTaggedCells(config=config)
    executor = ExecutePreprocessor()
    checker = CheckOutputs()

    nb = nbformat.v4.new_notebook(
        metadata={
            "papermill": {},
        },
        cells=[
            nbformat.v4.new_code_cell(
                "raise Exception('this cell should have been ignored')",
                metadata={"tags": ["no-execute"]},
            ),
            nbformat.v4.new_code_cell("print('Hello, world!')"),
            nbformat.v4.new_code_cell("for i in range(0, 100):\n    print(i)"),
        ],
    )
    resources = {"metadata": {"path": "test.ipynb"}}

    nb, resources = clearer.preprocess(nb, resources)
    nb, resources = executor.preprocess(nb, resources)

    assert checker.check_output(nb.cells[0])
    assert not checker.check_output(nb.cells[1])
