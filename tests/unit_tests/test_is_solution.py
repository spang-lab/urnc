from nbformat import notebooknode
from nbformat.notebooknode import NotebookNode
import urnc
import pytest
import click


def test_valid_solution_cell():
    cell = notebooknode.from_dict({"source": "### SOLUTION", "cell_type": "code"})
    assert urnc.preprocessor.add_tags.is_solution(cell)
