import filecmp
import re
import os
import subprocess

import freezegun
import conftest
import pytest
import git


@freezegun.freeze_time("2024-01-01 08:00:00 +0000")
@pytest.mark.slow
def test_urnc_student__data_science():
    outputs_dir = conftest.init_outputs_dir(
        test_module="regression",
        test_function="urnc_student",
        test_case=0,
        inputs=["data-science", "data-science-student-expected"],
        input_sources=[conftest.clone_data_science, conftest.clone_data_science_student]
    )
    cmd = f"{conftest.python} -m urnc student".split()
    cwd = f"{outputs_dir}/data-science"
    proc = subprocess.run(args=cmd, cwd=cwd)

    # Check results
    output = f"{outputs_dir}/data-science-student"
    git.Repo(output).git.clean("-xdf")
    expected = f"{outputs_dir}/data-science-student-expected"
    cmp = filecmp.dircmp(output, expected)
    assert all([
        proc.returncode == 0,
        cmp.diff_files == [],
        cmp.left_only == [],
        cmp.right_only == []
    ])


@freezegun.freeze_time("2024-01-01 08:00:00 +0100")
@pytest.mark.slow
def test_urnc_student__developer_skills():
    outputs_dir = conftest.init_outputs_dir(
        test_module="regression",
        test_function="urnc_student",
        test_case=1,
        inputs=["developer-skills", "developer-skills-student-expected"],
        input_sources=[conftest.clone_developer_skills, conftest.clone_developer_skills_student]
    )
    cmd = f"{conftest.python} -m urnc student".split()
    cwd = f"{outputs_dir}/developer-skills"
    proc = subprocess.run(args=cmd, cwd=cwd)

    # Check results
    output = f"{outputs_dir}/developer-skills-student"
    git.Repo(output).git.clean("-xdf")
    expected = f"{outputs_dir}/developer-skills-student-expected"
    cmp = filecmp.dircmp(output, expected)
    assert all([
        proc.returncode == 0,
        cmp.diff_files == [],
        cmp.left_only == [],
        cmp.right_only == []
    ])