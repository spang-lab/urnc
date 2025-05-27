import os
import shutil
from pathlib import Path

import git
import nbformat
import pytest

from urnc.init import init
from urnc.util import (branch_exists, chdir, dirs_equal, get_course_repo,
                       get_course_root, get_urnc_root, git_folder_name,
                       is_remote_git_url, read_notebook,
                       release_locks, tag_exists,
                       ensure_git_identity)


def test_read_notebook(tmp_path: Path):
    nb_path = tmp_path / "testnb.ipynb"
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_markdown_cell("# Test"))
    nbformat.write(nb, nb_path)
    nb2 = read_notebook(nb_path)
    assert nb2.cells[0].source == "# Test"


def test_is_remote_git_url(tmp_path: Path):
    assert is_remote_git_url("https://github.com/user/repo.git")
    assert is_remote_git_url("git@github.com:user/repo.git")
    assert is_remote_git_url("ssh://git@github.com/user/repo.git")
    assert not is_remote_git_url(".")
    assert not is_remote_git_url("repo")
    assert not is_remote_git_url("/local/path/to/repo")
    assert not is_remote_git_url("C:/local/path/to/repo")


def test_git_folder_name(tmp_path: Path):
    assert git_folder_name("https://github.com/user/xyz.git") == "xyz"
    assert git_folder_name("git@github.com:user/xyz.git") == "xyz"
    assert git_folder_name("https://github.com/user/xyz") == "xyz"
    assert git_folder_name("/some/path/to/xyz.git") == "xyz"
    assert git_folder_name("/some/path/to/xyz") == "xyz"


def test_branch_exists(tmp_path: Path):
    repo = git.Repo.init(tmp_path)
    repo.index.commit("init")
    repo.git.checkout('-b', 'feature')
    assert branch_exists(repo, 'feature')
    assert not branch_exists(repo, 'doesnotexist')


def test_tag_exists(tmp_path: Path):
    repo = git.Repo.init(tmp_path)
    repo.index.commit("init")
    repo.create_tag("v1.0.0")
    assert tag_exists(repo, "v1.0.0")
    assert not tag_exists(repo, "v2.0.0")


def test_get_course_repo(tmp_path: Path):
    init(path="example-course", template="full")
    # Call from within the course. Should return the repo object.
    with chdir("example-course/lectures"):
        repo = get_course_repo()
    assert repo.working_dir == str(tmp_path/"example-course")
    release_locks(repo)
    repo.__del__()
    # Call from outside the course. Should raise an exception.
    with pytest.raises(Exception, match="No 'config.yaml' found"):
        get_course_repo()
    # Remove .git folder and call again. Should raise an exception.
    shutil.rmtree(tmp_path/"example-course/.git", ignore_errors=True)
    with pytest.raises(Exception, match="not a git repo"):
        with chdir("example-course/lectures"):
            repo = get_course_repo()


def test_get_urnc_root(tmp_path: Path):
    os.makedirs(tmp_path/"urnc/sub", exist_ok=True)
    # Call from dir without pyproject.toml --> Exception
    with chdir(tmp_path/"urnc"):
        with pytest.raises(Exception, match="No 'pyproject.toml' found"):
            urnc_root = get_urnc_root()
    # Call from dir wrong pyproject.toml --> Exception
    (tmp_path/"pyproject.toml").write_text('[project]\nname = "noturnc"\n')
    with chdir(tmp_path/"urnc"):
        with pytest.raises(Exception, match="does not belong to the 'urnc' package"):
            urnc_root = get_urnc_root()
    # Call from dir with correct pyproject.toml
    (tmp_path/"urnc/pyproject.toml").write_text('[project]\nname = "urnc"\n')
    with chdir(tmp_path/"urnc/sub"):
        urnc_root = get_urnc_root()
    assert urnc_root == tmp_path/"urnc"


def test_get_course_root(tmp_path: Path):
    init(path="example-course", template="full")
    # Call from dir with config.yaml
    with chdir("example-course/lectures"):
        root = get_course_root()
    assert root == tmp_path/"example-course"
    # Call from dir without config.yaml. Should raise Exception.
    os.remove(tmp_path/"example-course/config.yaml")
    with pytest.raises(Exception, match="No 'config.yaml' found"):
        with chdir("example-course/lectures"):
            root = get_course_root()


def test_dirs_equal(tmp_path: Path):
    dirs = [tmp_path/"one", tmp_path/"two"]
    for dir in dirs:
        dir.mkdir()
        (dir/"file.txt").write_text("hello")
        (dir/"sub").mkdir()
        (dir/"sub"/"subfile.txt").write_text("subcontent")
        (dir/".hidden").mkdir()
    assert dirs_equal(dirs[0], dirs[1]), "Check 0"
    (dirs[0]/"file.txt").write_text("changed")
    assert not dirs_equal(dirs[0], dirs[1]), "Check 1"
    (dirs[1]/"file.txt").write_text("changed")
    assert dirs_equal(dirs[0], dirs[1]), "Check 2"
    (dirs[0]/"newfile.txt").write_text("new")
    assert not dirs_equal(dirs[0], dirs[1]), "Check 3"
    (dirs[1]/"newfile.txt").write_text("new")
    assert dirs_equal(dirs[0], dirs[1]), "Check 4"
    (dirs[0]/".hidden"/"hiddenfile.txt").write_text("hidden")
    assert dirs_equal(dirs[0], dirs[1]) == True, "Check 5"
    assert not dirs_equal(dirs[0], dirs[1], dotignore=False), "Check 6"


def test_ensure_git_identity(tmp_path: Path):

    # Initialize repo and git config.
    repo = git.Repo.init(tmp_path)
    with repo.config_writer() as config:
        config.set_value("user", "name", "Dummy Name")
        config.set_value("user", "email", "dummy.name@dummydomain.com")

    # User and email are already set, so nothing should change.
    ensure_git_identity(repo)
    with repo.config_reader() as config:
        name = config.get_value("user", "name")
        email = config.get_value("user", "email")
    assert name == "Dummy Name"
    assert email == "dummy.name@dummydomain.com"

    # Update with force. Now user and email should get updated.
    ensure_git_identity(repo, force=True)
    with repo.config_reader() as config:
        name = config.get_value("user", "name")
        email = config.get_value("user", "email")
    assert name == "urnc"
    assert email == "urnc@spang-lab.de"
