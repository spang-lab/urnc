from os import chdir, getcwd, listdir
from os.path import abspath, isdir, normpath
import git
import urnc
import filecmp
from conftest import *


def test_urnc_ci_ci__with_solutions():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci",
        test_function="ci",
        test_case=0,
        inputs=["minimal-course"],
        input_sources=["tests/inputs/minimal-course"]
    )
    with urnc.util.chdir(f"{outputs_dir}/minimal-course"):
        urnc.ci.ci(commit=False)
    output = f"{outputs_dir}/minimal-course-student"
    expect = "tests/expected/minimal-course-student"
    out_only, exp_only, diff, _ = compare_dirs(output, expect)
    assert all((out_only == set(),
                exp_only == set(),
                diff == set()))


def test_urnc_ci_ci__no_solutions():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci",
        test_function="ci",
        test_case=1,
        inputs=["minimal-course"],
        input_sources=["tests/inputs/minimal-course"]
    )
    with urnc.util.chdir(f"{outputs_dir}/minimal-course"):
        disable_solution_generation()
        urnc.ci.ci(commit=False)
    output = f"{outputs_dir}/minimal-course-student"
    expect = "tests/expected/minimal-course-student"
    out_only, exp_only, diff, _ = compare_dirs(output, expect)
    assert all((out_only == set(),
                all("solutions" in s for s in exp_only),
                diff == {"config.yaml"}))