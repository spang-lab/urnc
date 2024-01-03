import filecmp
import os
import shutil

import conftest
import urnc

cwd = os.getcwd()  # cwd is repo root when started via pytest
test_module = "urnc.convert"
test_function = "convert"


def setup_module():
    if False:
        # Enable logging for debugging
        urnc.logger.setup_logger(use_file=False, verbose=True)


def test_convert__inNB_solF_forceF_dryF_outExistF_solExistF():
    test_case = 0
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    output = f"{outputs_dir}/urnc.ipynb"
    expected = "tests/expected/minimal-course-converted/lectures/urnc.ipynb"
    urnc.convert.convert(input=input, output=outputs_dir, ask=False)
    assert filecmp.cmp(output, expected)


def test_convert__inNB_solF_forceF_dryF_outExistT_solExistF():
    test_case = 1
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    output = f"{outputs_dir}/urnc.ipynb"
    open(output, "w").write("Some text")
    urnc.convert.convert(input=input, output=outputs_dir, ask=False)
    assert open(output, "r").read() == "Some text"


def test_convert__inNB_solF_forceT_dryF_outExistT_solExistF():
    test_case = 2
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    output = f"{outputs_dir}/urnc.ipynb"
    expected = "tests/expected/minimal-course-converted/lectures/urnc.ipynb"
    open(output, "w").write("Some text")
    urnc.convert.convert(input=input, output=outputs_dir, force=True, ask=False)
    assert filecmp.cmp(output, expected)


def test_convert__inDir_solF_forceF_dryF_outExistF_solExistF():
    test_case = 3
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures"
    expected = "tests/expected/minimal-course-converted/lectures"
    urnc.convert.convert(input=input, output=outputs_dir, ask=False)
    cmp = filecmp.dircmp(outputs_dir, expected)
    assert all((cmp.diff_files == [], cmp.left_only == [], cmp.right_only == []))

# Solution True


def test_convert__inNB_solT_forceF_dryF_outExistF_solExistF():
    test_case = 4
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    expects_dir = "tests/expected/minimal-course-converted-with-solutions/lectures"
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    outputs = [f"{outputs_dir}/urnc.ipynb", f"{outputs_dir}/urnc-solution.ipynb"]
    expects = [f"{expects_dir}/urnc.ipynb", f"{expects_dir}/urnc-solution.ipynb"]
    urnc.convert.convert(input=input, output=outputs_dir, solution=outputs_dir, ask=False)
    assert all([
        filecmp.cmp(outputs[0], expects[0]),
        filecmp.cmp(outputs[1], expects[1])
    ])


def test_convert__inNB_solT_forceF_dryF_outExistT_solExistT():
    test_case = 5
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    outputs = [f"{outputs_dir}/urnc.ipynb", f"{outputs_dir}/urnc-solution.ipynb"]
    open(outputs[0], "w").write("abc")
    open(outputs[1], "w").write("123")
    urnc.convert.convert(input=input, output=outputs_dir, solution=outputs_dir, ask=False)
    assert all([
        open(outputs[0], "r").read() == "abc",
        open(outputs[1], "r").read() == "123"
    ])


def test_convert__inNB_solT_forceT_dryF_outExistT_solExistT():
    test_case = 6
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    expects_dir = "tests/expected/minimal-course-converted-with-solutions/lectures"
    input = "tests/inputs/minimal-course/lectures/urnc.ipynb"
    outputs = [f"{outputs_dir}/urnc.ipynb", f"{outputs_dir}/urnc-solution.ipynb"]
    expects = [f"{expects_dir}/urnc.ipynb", f"{expects_dir}/urnc-solution.ipynb"]
    open(outputs[0], "w").write("abc")
    open(outputs[1], "w").write("123")
    urnc.convert.convert(input=input, output=outputs_dir, solution=outputs_dir, force=True, ask=False)
    assert all([filecmp.cmp(outputs[0], expects[0]),
                filecmp.cmp(outputs[1], expects[1])])


def test_convert__inDir_solT_forceF_dryF_outExistF_solExistF():
    test_case = 7
    input = "tests/inputs/minimal-course"
    outputs_dir = conftest.init_outputs_dir(test_module, test_function, test_case)
    expects_dir = "tests/expected/minimal-course-converted-with-solutions"
    urnc.convert.convert(input=input, output=outputs_dir, solution=outputs_dir, ask=False)
    cmp = filecmp.dircmp(outputs_dir, expects_dir)
    assert all((cmp.diff_files == [],
                cmp.left_only == [],
                cmp.right_only == []))
