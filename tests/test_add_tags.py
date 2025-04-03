from traitlets.config import Config
import urnc
from urnc.preprocessor import util
import urnc.preprocessor.add_tags as add_tags
import pytest
import click

import nbformat


def test_md_headers():
    cell = nbformat.v4.new_markdown_cell("# Header 1")
    level, title, id = add_tags.extract_header(cell)
    assert level == 1 and title == "Header 1" and id == "header_1"
    cell2 = nbformat.v4.new_markdown_cell("## Header 2")
    level, title, id = add_tags.extract_header(cell2)
    assert level == 2 and title == "Header 2" and id == "header_2"
    cell3 = nbformat.v4.new_markdown_cell("##      Header 2")
    level, title, id = add_tags.extract_header(cell3)
    assert level == 2 and title == "Header 2" and id == "header_2"


def test_html_headers():
    cell = nbformat.v4.new_markdown_cell("<h1>Header 1</h1>")
    level, title, id = add_tags.extract_header(cell)
    assert level == 1 and title == "Header 1" and id == "header_1"

    cell2 = nbformat.v4.new_markdown_cell("<h2>Header 2</h2>")
    level, title, id = add_tags.extract_header(cell2)
    assert level == 2 and title == "Header 2" and id == "header_2"
    cell3 = nbformat.v4.new_markdown_cell("<h2>      Header 2</h2>")
    level, title, id = add_tags.extract_header(cell3)
    assert level == 2 and title == "Header 2" and id == "header_2"
    cell4 = nbformat.v4.new_markdown_cell("<h2>      Header \n2</h2>")
    level, title, id = add_tags.extract_header(cell4)
    assert level == 2 and title == "Header \n2" and id == "header_2"


def test_styled_headers():
    cell = nbformat.v4.new_markdown_cell(
        '<h3 style="color: #d97706; font-size: 2em">Assignment test</h3>")'
    )
    level, title, id = add_tags.extract_header(cell)
    assert level == 3 and title == "Assignment test" and id == "assignment_test"

    cell = nbformat.v4.new_markdown_cell(
        '<h3 style="color: #047857; font-size: 2em">LAB 16</h3>'
    )
    level, title, id = add_tags.extract_header(cell)
    assert level == 3 and title == "LAB 16" and id == "lab_16"

    cell = nbformat.v4.new_markdown_cell(
        '<h3 style="color: #d97706; font-size: 2em">The following is for you to practice at home, but is not part of the official assignment.</h3>'
    )
    level, title, id = add_tags.extract_header(cell)
    assert level == 3
    assert not util.starts_with(title, ["assignment"])


def test_code_cell():
    cell = nbformat.v4.new_code_cell("print('Hello World!')")
    level, title, id = add_tags.extract_header(cell)
    assert level is None and title is None and id is None
    cell2 = nbformat.v4.new_code_cell("# Solution")
    level, title, id = add_tags.extract_header(cell2)
    assert level == 1 and title == "Solution" and id == "solution"
    cell3 = nbformat.v4.new_code_cell("### Skeleton")
    level, title, id = add_tags.extract_header(cell3)
    assert level == 3 and title == "Skeleton" and id == "skeleton"


def test_full_notebook():
    cells = [
        nbformat.v4.new_markdown_cell("# Assignment 1"),
        nbformat.v4.new_code_cell("print('Hello World!')"),
        nbformat.v4.new_markdown_cell("# Solution 1"),
        nbformat.v4.new_code_cell("### Solution print('Hello World!')"),
        nbformat.v4.new_markdown_cell("# Random Header"),
    ]
    nb = nbformat.v4.new_notebook(cells=cells)
    preprocessor = add_tags.AddTags()
    tagged, _ = preprocessor.preprocess(nb, {})
    assert add_tags.util.has_tags(tagged.cells[0], ["assignment-start", "assignment"])
    assert add_tags.util.has_tags(tagged.cells[1], ["assignment"])
    assert add_tags.util.has_tags(tagged.cells[2], ["solution", "assignment"])
    assert add_tags.util.has_tags(tagged.cells[3], ["solution", "assignment"])
    assert add_tags.util.has_tag(tagged.cells[4], "assignment") is False


def test_solution_comment():
    cells = [
        nbformat.v4.new_code_cell("# Enter solution here"),
    ]
    nb = nbformat.v4.new_notebook(cells=cells)
    preprocessor = add_tags.AddTags()
    tagged, _ = preprocessor.preprocess(nb, {})
    assert not add_tags.util.has_tag(tagged.cells[0], "solution")


def test_custom_keywords():
    cells = [
        nbformat.v4.new_markdown_cell("# Lab 1"),
        nbformat.v4.new_code_cell("print('Hello World!')"),
        nbformat.v4.new_markdown_cell("# Random Header"),
        nbformat.v4.new_markdown_cell("# Assignment 1"),
    ]
    nb = nbformat.v4.new_notebook(cells=cells)
    config = Config()
    config.AddTags.assignment_keywords = ["Lab", "Assignment"]
    config.AddTags.assignment_start_tag = "lab-start"
    config.AddTags.assignment_tag = "lab"
    preprocessor = add_tags.AddTags(config=config)
    tagged, _ = preprocessor.preprocess(nb, {})
    assert add_tags.util.has_tags(tagged.cells[0], ["lab-start", "lab"])
    assert add_tags.util.has_tags(tagged.cells[1], ["lab"])
    assert add_tags.util.has_tag(tagged.cells[2], "lab") is False
    assert add_tags.util.has_tags(tagged.cells[3], ["lab-start", "lab"])
