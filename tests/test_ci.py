import copy
import pathlib

import click
import git
import pytest
import nbformat
import urnc
import urnc.preprocessor.util


def test_ci(tmp_path: pathlib.Path):
    course_name = "Example Course"
    admin_path = tmp_path / "example-course-admin"
    admin_url = tmp_path / "example-course-admin.git"
    student_path = tmp_path / "example-course"
    student_url = tmp_path / "example-course.git"
    urnc.init.init(course_name, admin_path, admin_url, student_url)

    config = urnc.config.read(admin_path)
    config["convert"]["write_mode"] = "overwrite"
    config["ci"]["commit"] = True
    urnc.ci.ci(config)
    urnc.pull.pull(str(student_url), str(student_path), "main", 1)

    nb = nbformat.read(student_path / "example.ipynb", as_version=4)
    cells = nb["cells"]
    print(cells)
    assert urnc.preprocessor.util.has_tag(cells[2], "assignment")
    assert urnc.preprocessor.util.has_tag(cells[2], "assignment-start")
    assert urnc.preprocessor.util.has_tag(cells[3], "assignment")
    assert not (student_path / "config.yaml").exists()


def test_clone_student_repo(tmp_path: pathlib.Path):

    print(f"")
    print(f"- Testdir: {tmp_path}")
    print(f"- Initializing example course")
    course_name = "Example Course"
    admin_path = tmp_path/"example-course-admin"
    admin_url = tmp_path/"example-course-admin.git"
    student_path = tmp_path/"example-course-admin/out"
    student_url = tmp_path/"example-course-student.git"
    urnc.init.init(course_name, admin_path, admin_url, student_url)
    assert admin_path.exists() == True,  "Admin path should exist"
    assert admin_url.exists() == True,  "Admin URL should exist"
    assert student_path.exists() == False, "Student path should not exist yet"
    assert student_url.exists() == True,  "Student URL should exist"

    print("- Testing normal case where everything should work as expected")
    config = urnc.config.read_config(admin_path)
    urnc.ci.clone_student_repo(config)
    assert student_path.exists() == True, "Student path should exist after cloning"

    print("- Testing clone with undefined 'git.student' field in config")
    config_copy = copy.deepcopy(config)
    config_copy["git"]["student"] = None
    with pytest.raises(click.UsageError, match="No .* git.student .* in config"):
        urnc.ci.clone_student_repo(config_copy)

    print("- Testing clone with existing out dir that is no repo")
    urnc.util.rmtree(student_path/".git")
    with pytest.raises(Exception, match="Folder .* exists but is not a git repo"):
        urnc.ci.clone_student_repo(config)

    print("- Testing clone with existing repo that has a different remote URL")
    student_repo = git.Repo.init(student_path, initial_branch="main")
    student_repo.create_remote("origin", "https://example.com/other-repo.git")
    with pytest.raises(Exception, match="Repo remote mismatch"):
        urnc.ci.clone_student_repo(config)


def test_write_gitignore(tmp_path: pathlib.Path):

    print(f"")
    print(f"- Testdir: {tmp_path}")
    student_gitignore = tmp_path/".gitignore.student"
    main_gitignore = tmp_path/".gitignore.main"
    main_gitignore.write_text("config.yml\n")

    print("- Testing normal case. No errors expected.")
    config = {
        "git": {
            "exclude": [
                "*.pyc",
                {"pattern": "!foo.txt", "after": "2999-01-01 00:00 CEST"},
                {"pattern": "!bar.txt", "until": "2000-01-01 00:00 CEST"}
            ]
        }
    }
    urnc.ci.write_gitignore(main_gitignore, student_gitignore, config)
    content = student_gitignore.read_text()
    assert "config.yml" in content
    assert "*.pyc" in content
    assert "!foo.txt" not in content  # after future date
    assert "!bar.txt" not in content  # until past date

    print("- Testing broken config. This should raise an exception.")
    config = {"git": {"exclude": "not a list"}}
    with pytest.raises(Exception, match="config.git.exclude must be a list"):
        urnc.ci.write_gitignore(None, student_gitignore, config)

