import filecmp
import os
import shutil

import conftest
import urnc

cwd = os.getcwd() # cwd is repo root when started via pytest
test_module = "urnc.convert"
test_function = "convert"

def setup_module():
    if False:
        # Enable logging for debugging
        urnc.logger.setup_logger(use_file = False, verbose = True)

def test_convert__inNB_solF_forceF_dryF_outExistF_solExistF():
    test_case = 0
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    output = f"{outputs_dir}/urnc.ipynb"
    expected = "tests/expected/minimal-course-converted/lectures/urnc.ipynb"
    urnc.convert.convert(input=input, output=outputs_dir)
    assert filecmp.cmp(output, expected)

def test_convert__inNB_solF_forceF_dryF_outExistT_solExistF():
    test_case = 1
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    output = f"{outputs_dir}/urnc.ipynb"
    open(output, "w").write("Some text")
    urnc.convert.convert(input=input, output=outputs_dir)
    assert open(output, "r").read() == "Some text"

def test_convert__inNB_solF_forceT_dryF_outExistT_solExistF():
    test_case = 2
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    output = f"{outputs_dir}/urnc.ipynb"
    expected = "tests/expected/minimal-course-converted/lectures/urnc.ipynb"
    open(output, "w").write("Some text")
    urnc.convert.convert(input=input, output=outputs_dir, force=True)
    assert filecmp.cmp(output, expected)

def test_convert__inDir_solF_forceF_dryF_outExistF_solExistF():
    test_case = 3
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures"
    expected = "tests/expected/minimal-course-converted/lectures"
    urnc.convert.convert(input=input, output=outputs_dir)
    cmp = filecmp.dircmp(outputs_dir, expected)
    assert all((cmp.diff_files == [], cmp.left_only == [], cmp.right_only == []))
