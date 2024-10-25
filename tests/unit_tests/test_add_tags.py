from nbformat import notebooknode
from nbformat.notebooknode import NotebookNode
import urnc.preprocessor.add_tags as add_tags
import pytest
import click


def test_md_headers():
    cell = notebooknode.from_dict({"source": "# Header 1", "cell_type": "markdown"})
    level, title, id = add_tags.extract_header(cell)
    assert level == 1 and title == "Header 1" and id == "header_1"
    cell2 = notebooknode.from_dict({"source": "## Header 2", "cell_type": "markdown"})
    level, title, id = add_tags.extract_header(cell2)
    assert level == 2 and title == "Header 2" and id == "header_2"
    cell3 = notebooknode.from_dict(
        {"source": "##      Header 2", "cell_type": "markdown"}
    )
    level, title, id = add_tags.extract_header(cell3)
    assert level == 2 and title == "Header 2" and id == "header_2"


def test_html_headers():
    cell = notebooknode.from_dict(
        {"source": "<h1>Header 1</h1>", "cell_type": "markdown"}
    )
    level, title, id = add_tags.extract_header(cell)
    assert level == 1 and title == "Header 1" and id == "header_1"

    cell2 = notebooknode.from_dict(
        {"source": "<h2>Header 2</h2>", "cell_type": "markdown"}
    )
    level, title, id = add_tags.extract_header(cell2)
    assert level == 2 and title == "Header 2" and id == "header_2"
    cell3 = notebooknode.from_dict(
        {"source": "<h2>      Header 2</h2>", "cell_type": "markdown"}
    )
    level, title, id = add_tags.extract_header(cell3)
    assert level == 2 and title == "Header 2" and id == "header_2"
    cell4 = notebooknode.from_dict(
        {"source": "<h2>      Header \n2</h2>", "cell_type": "markdown"}
    )
    level, title, id = add_tags.extract_header(cell4)
    assert level == 2 and title == "Header \n2" and id == "header_2"


def test_code_cell():
    cell = notebooknode.from_dict(
        {"source": "print('Hello World!')", "cell_type": "code"}
    )
    level, title, id = add_tags.extract_header(cell)
    assert level is None and title is None and id is None
    cell2 = notebooknode.from_dict({"source": "# Header", "cell_type": "code"})
    level, title, id = add_tags.extract_header(cell2)
    assert level == 1 and title == "Header" and id == "header"
