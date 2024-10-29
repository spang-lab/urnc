from urnc import execute
import nbformat


def test_execute_notebook():
    config = {
        "version": None,
        "base_path": "/path/to/course",
        "convert": {"write_mode": "skip-existing", "targets": []},
    }
    nb = nbformat.v4.new_notebook(
        metadata={
            "papermill": {},
        },
        cells=[
            nbformat.v4.new_code_cell("print('Hello, world!')"),
        ],
    )

    ex_nb = execute.execute_notebook(config, nb)
    assert ex_nb.cells[0].outputs[0]["text"] == "Hello, world!\n"


def test_execute_error():
    config = {
        "version": None,
        "base_path": "/path/to/course",
        "convert": {"write_mode": "skip-existing", "targets": []},
    }
    nb = nbformat.v4.new_notebook(
        metadata={
            "papermill": {},
        },
        cells=[
            nbformat.v4.new_code_cell("print('Hello, world!'"),
        ],
    )

    ex_nb = execute.execute_notebook(config, nb)
    assert ex_nb.cells[0].outputs[0]["ename"] == "SyntaxError"

