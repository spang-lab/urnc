from os import chdir, getcwd, listdir
from os.path import abspath, isdir, normpath
import git
import urnc
from conftest import *


def test_urnc_ci_clone_student_repo__urlMissing_repoMissing():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci",
        test_function="clone_student_repo",
        test_case=0,
        inputs=["minimal-course"],
        input_sources=["tests/inputs/minimal-course"]
    )
    with urnc.util.chdir(f"{outputs_dir}/minimal-course"):
        git.Repo.init() # urnc courses must be git repos (for now)
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
    assert normpath(repo.working_dir) == normpath(f"{outputs_dir}/minimal-course-student")


def test_urnc_ci_clone_student_repo__urlMissing_repoExists():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci",
        test_function="clone_student_repo",
        test_case=1,
        inputs=["minimal-course"],
        input_sources=["tests/inputs/minimal-course"]
    )
    with urnc.util.chdir(outputs_dir):
        git.Repo.init("minimal-course-student")
    with urnc.util.chdir(f"{outputs_dir}/minimal-course"):
        git.Repo.init() # urnc courses must be git repos (for now)
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
    assert normpath(repo.working_dir) == normpath(f"{outputs_dir}/minimal-course-student")


def test_urnc_ci_clone_student_repo__urlExists_repoMissing():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci",
        test_function="clone_student_repo",
        test_case=2,
        inputs=["urnc-example-course"],
        input_sources=[clone_urnc_example_course]
    )
    with urnc.util.chdir(f"{outputs_dir}/urnc-example-course"):
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
    assert normpath(repo.working_dir) == normpath(f"{outputs_dir}/urnc-example-course-public")


def test_urnc_ci_clone_student_repo__urlExists_falseRepoExists():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci",
        test_function="clone_student_repo",
        test_case=3,
        inputs=["urnc-example-course"],
        input_sources=[clone_urnc_example_course]
    )
    with urnc.util.chdir(outputs_dir):
        git.Repo.init("urnc-example-course-public")
    exception_raised = False
    try:
        with urnc.util.chdir(f"{outputs_dir}/urnc-example-course"):
            config = urnc.util.read_config()
            repo = urnc.ci.clone_student_repo(config)
    except Exception as e:
        exception_raised = True
    assert exception_raised


def test_urnc_ci_clone_student_repo__urlExists_correctRepoExists():
    outputs_dir = init_outputs_dir(
        test_module="urnc.ci",
        test_function="clone_student_repo",
        test_case=4,
        inputs=["urnc-example-course", "urnc-example-course-public"],
        input_sources=[clone_urnc_example_course, clone_urnc_example_course_public]
    )
    with urnc.util.chdir(f"{outputs_dir}/urnc-example-course"):
        config = urnc.util.read_config()
        repo = urnc.ci.clone_student_repo(config)
    assert normpath(repo.working_dir) == normpath(f"{outputs_dir}/urnc-example-course-public")
