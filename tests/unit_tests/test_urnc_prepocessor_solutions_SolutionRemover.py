import os

import conftest
import nbformat
import traitlets
from nbconvert.exporters.notebook import NotebookExporter

from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.solutions import SolutionRemover

cwd = os.getcwd()  # cwd is repo root when started via pytest
test_module = "urnc.preprocessor.solutions"
test_function = "SolutionRemover"

preprocessors = [AddTags, SolutionRemover]
config = traitlets.config.Config()
config.NotebookExporter.preprocessors = preprocessors
converter = NotebookExporter(config)

def test_urnc_preprocessor_solutions_SolutionRemover():
    input = "tests/inputs/minimal-course/lectures/fibonacci.ipynb"
    input_nb = nbformat.read(input, as_version=4)
    output_str = converter.from_notebook_node(input_nb)[0]
    expect = "tests/expected/minimal-course-converted/lectures/fibonacci.ipynb"
    expect_str = open(expect).read()
    assert output_str == expect_str
