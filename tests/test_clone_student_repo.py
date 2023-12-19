from os import chdir, getcwd
from os.path import abspath, isdir
from shutil import rmtree

import git

import urnc

cwd = getcwd()
test_course = "tests/courses/minimal"
test_course_git = "tests/courses/minimal/.git"
test_course_student = f"{abspath(test_course)}-student"

def setup_module(module):
    """Make sure the used test course is a git repo, as we don't commit the .git folders from the test courses. This function is run once before all tests in this module."""
    if isdir(test_course) and not isdir(test_course_git):
        git.Repo.init(test_course)

def test_clone_student_repo_url_missing_repo_missing():
    try:
        if isdir(test_course_student):
            rmtree(test_course_student)
        chdir("tests/courses/minimal")
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
        assert repo.working_dir == test_course_student
    finally:
        chdir(cwd)

def test_clone_student_repo_url_missing_repo_exists():
    try:
        assert isdir(test_course_student), "The student repo should already exist, as it was created by the previous test"
        chdir("tests/courses/minimal")
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
        assert repo.working_dir == test_course_student
    finally:
        chdir(cwd)

def test_clone_student_repo_url_exists_repo_missing():
    pass

def test_clone_student_repo_url_exists_repo_exists():
    pass

