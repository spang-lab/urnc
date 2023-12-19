from os import chdir, getcwd
from os.path import abspath, isdir

import git

import urnc
from urnc.test import rmtree

cwd = getcwd()
minimal_course = abspath("tests/courses/minimal")
minimal_course_git = f"{minimal_course}/.git"
minimal_course_student = f"{minimal_course}-student"
example_course = abspath("tests/courses/urnc-example-course")
example_course_url = "https://github.com/spang-lab/urnc-example-course"
example_course_git = f"{example_course}/.git"
example_course_student = f"{example_course}-public"

def setup_module(module):
    """Make sure the used test course is a git repo, as we don't commit the .git folders from the test courses. This function is run once before all tests in this module."""
    if isdir(minimal_course) and not isdir(minimal_course_git):
        git.Repo.init(minimal_course)
    if isdir(example_course):
        if not isdir(example_course_git):
            rmtree(example_course)
            git.Repo.clone_from(url=example_course_url, to_path=example_course)
    else:
        git.Repo.clone_from(url=example_course_url, to_path=example_course)
    git.Repo(example_course).git.checkout("9c277cdc7c7985f433f2c7f6fabcba1eefd2f844")


def test_clone_student_repo_url_missing_repo_missing():
    try:
        if isdir(minimal_course_student):
            rmtree(minimal_course_student)
        chdir(minimal_course)
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
        assert repo.working_dir == minimal_course_student
    finally:
        chdir(cwd)

def test_clone_student_repo_url_missing_repo_exists():
    try:
        msg = "Student repo should exist, as it was created by previous test"
        assert isdir(minimal_course_student), msg
        chdir(minimal_course)
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
        assert repo.working_dir == minimal_course_student
    finally:
        chdir(cwd)

def test_clone_student_repo_url_exists_repo_missing():
    try:
        if isdir(example_course_student):
            rmtree(example_course_student)
        chdir(example_course)
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
        assert repo.working_dir == example_course_student
    finally:
        chdir(cwd)

def test_clone_student_repo_url_exists_repo_exists():
    try:
        msg = "Student repo should exist, as it was created by previous test"
        assert isdir(example_course_student), msg
        chdir(example_course)
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
        assert repo.working_dir == example_course_student
    finally:
        chdir(cwd)


