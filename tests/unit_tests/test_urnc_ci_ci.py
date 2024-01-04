from os import chdir, getcwd, listdir
from os.path import abspath, isdir, normpath
import git
import urnc
from conftest import *


def test_urnc_ci_ci():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci", test_function="ci", test_case=0,
        inputs=["minimal-course"],
        input_sources=["tests/inputs/minimal-course"]
    )
    with urnc.util.chdir(f"{outputs_dir}/minimal-course"):
        urnc.ci.ci(commit=False)
    assert True
