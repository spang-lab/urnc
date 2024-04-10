import sys
import subprocess

import conftest
import pytest
import git


@pytest.mark.slow
def test_urnc_student__data_science():
    outputs_dir = conftest.init_outputs_dir(
        test_module="regression",
        test_function="urnc_student",
        test_case="0",
        inputs=["data-science", "data-science-student-expected"],
        input_sources=[conftest.clone_data_science, conftest.clone_data_science_student]
    )
    cmd = f"{sys.executable} -m urnc student".split()
    cwd = f"{outputs_dir}/data-science"
    proc = subprocess.run(args=cmd, cwd=cwd)

    # Check results
    output = f"{outputs_dir}/data-science-student"
    git.Repo(output).git.clean("-xdf")
    expected = f"{outputs_dir}/data-science-student-expected"
    left_only, right_only, diff_size, same_size = conftest.compare_dirs(output, expected)
    left_only = [path.replace("\\", "/") for path in left_only]
    print("left_only", left_only)
    print("right_only", right_only)
    assert all([
        proc.returncode == 0,
        left_only == {'tutorials/Tutorial_10.ipynb', 'tutorials/Tutorial_11.ipynb'},
        right_only == set(),
        diff_size == set()
    ])


@pytest.mark.slow
def test_urnc_student__developer_skills():
    outputs_dir = conftest.init_outputs_dir(
        test_module="regression",
        test_function="urnc_student",
        test_case="1",
        inputs=["developer-skills", "developer-skills-student-expected"],
        input_sources=[conftest.clone_developer_skills, conftest.clone_developer_skills_student]
    )
    cmd = f"{sys.executable} -m urnc student".split()
    cwd = f"{outputs_dir}/developer-skills"
    proc = subprocess.run(args=cmd, cwd=cwd)

    # Check results
    output = f"{outputs_dir}/developer-skills-student"
    git.Repo(output).git.clean("-xdf")
    expected = f"{outputs_dir}/developer-skills-student-expected"
    left_only, right_only, diff_size, same_size = conftest.compare_dirs(output, expected)
    assert all([
        proc.returncode == 0,
        left_only == set(),
        right_only == set(),
        diff_size == set()
    ])