import copy
import pathlib

import click
import git
import pytest
import nbformat
import urnc
import urnc.preprocessor.util
import urnc.logger

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
YELLOW = "\033[33m"

def heading(text: str):
    """Prints a heading with a specific format."""
    print(f"{RED}{text}{RESET}")

def test_ci_ci(tmp_path: pathlib.Path):

    heading("\n1. SETUP LOCAL ADMIN REPO, REMOTE ADMIN REPO AND REMOTE STUDENT REPO")
    course_name = "Example Course"
    admin_path = tmp_path / "example-course-admin" # contains .git/, .gitignore, config.yaml, example.ipynb
    admin_url = tmp_path / "example-course-admin.git" # bare repo used as remote for admin repo
    student_path = tmp_path / "example-course" # will be created by urnc.pull.pull
    student_url = tmp_path / "example-course.git" # bare repo used as remote for student repo
    urnc.init.init(course_name, admin_path, admin_url, student_url)

    heading("2. DO FIRST CI RUN")
    config = urnc.config.read(admin_path)
    config["convert"]["write_mode"] = "overwrite"
    config["ci"]["commit"] = True
    config_bak = copy.deepcopy(config) # store for later check
    urnc.ci.ci(config)

    heading("3. PULL AND CHECK LOCAL STUDENT REPO")
    urnc.pull.pull(str(student_url), str(student_path), "main", 1)
    nb = nbformat.read(student_path / "example.ipynb", as_version=4)
    cells = nb["cells"]
    assert urnc.preprocessor.util.has_tag(cells[2], "assignment")
    assert urnc.preprocessor.util.has_tag(cells[2], "assignment-start")
    assert urnc.preprocessor.util.has_tag(cells[3], "assignment")
    assert not (student_path / "config.yaml").exists()

    heading("4. DO SECOND CI RUN (no push expected because we did not change anything)")
    old_stud_hist = git.Repo(student_path).git.log("--oneline")
    urnc.ci.ci(config)
    urnc.pull.pull(str(student_url), str(student_path), "main", 1)
    new_stud_hist = git.Repo(student_path).git.log("--oneline")
    assert old_stud_hist == new_stud_hist, "Calling CI should not create a commit if nothing changed"
    assert config == config_bak, "Calling CI should not change the config (fixed with 2.3.1)"

    heading("5. DO THIRD CI RUN (we add one file, so we expect a push)")
    (admin_path / "new_file.txt").write_text("This is a new file.")
    old_stud_hist = git.Repo(student_path).git.log("--oneline")
    n_commits_old = len(old_stud_hist.split('\n'))
    urnc.ci.ci(config)
    urnc.pull.pull(str(student_url), str(student_path), "main", 1)
    new_stud_hist = git.Repo(student_path).git.log("--oneline")
    n_commits_new = len(new_stud_hist.split('\n'))
    assert n_commits_new == n_commits_old + 1, "Calling CI should create a new commit after adding a file"

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

