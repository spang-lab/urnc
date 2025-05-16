from pathlib import Path
from tempfile import mkdtemp

import os
import git

from urnc.config import read_config
from urnc.init import init
from urnc.util import chdir


def test_init_with_default_args():
    tmp_path = Path(mkdtemp())
    with chdir(tmp_path):
        repo = init(name="Test Course")
        config = read_config("test_course")
    admin_path = Path(repo.git_dir).parent
    config = read_config(admin_path)
    # Check created files
    assert admin_path.exists()
    assert len(os.listdir(tmp_path)) == 1
    # Check local admin repo
    assert isinstance(repo, git.Repo)
    assert not repo.bare
    assert repo.remotes == []
    assert len(list(repo.iter_commits())) == 1
    # Check config
    assert config.get("name", "") == "Test Course"
    assert config.get("git", {}).get("student", "") == "Link to student repo"


def test_init_with_remote_urls():
    tmp_path = Path(mkdtemp())
    course_name = "Test Course"
    admin_path = tmp_path / "course"
    admin_url = "git@github.com:example-user/test-course.git"
    student_url = "git@github.com:example-user/test-course-public.git"
    repo = init(course_name, admin_path, admin_url, student_url)
    config = read_config(admin_path)
    # Check created files
    assert admin_path.exists()
    assert len(os.listdir(tmp_path)) == 1
    # Check local admin repo
    assert isinstance(repo, git.Repo)
    assert not repo.bare
    assert len(list(repo.iter_commits())) == 1
    assert [r.name for r in repo.remotes] == ["origin"]
    assert repo.remotes["origin"].url == str(admin_url)
    # Check config
    assert config.get("name", "") == "Test Course"
    assert config.get("git", {}).get("student", "") == str(student_url)


def test_init_with_local_urls():
    tmp_path = Path(mkdtemp())
    course_name = "Test Course"
    admin_path = tmp_path / "test-course-admin"
    admin_url = tmp_path / "test-course-admin.git"
    student_url = tmp_path / "test-course.git"
    repo = init(course_name, admin_path, admin_url, student_url)
    config = read_config(admin_path)

    # Check created files
    assert admin_path.exists()
    assert admin_url.exists()
    assert student_url.exists()
    assert len(os.listdir(tmp_path)) == 3
    # Check local admin repo
    assert isinstance(repo, git.Repo)
    assert not repo.bare
    assert len(list(repo.iter_commits())) == 1
    assert [r.name for r in repo.remotes] == ["origin"]
    assert repo.remotes["origin"].url == str(admin_url).replace("\\", "/")
    # Check remote admin repo
    assert git.Repo(admin_url).bare
    # Check remote student repo
    assert git.Repo(student_url).bare
    # Check config
    assert config.get("name", "") == "Test Course"
    assert config.get("git", {}).get("student", "") == str(student_url)

    repo.git.clear_cache() # (1)
    # (1) Required on Windows because gitPython is buggy and doesn't clean up open file handles.
    # For details see: https://github.com/gitpython-developers/GitPython/issues?q=label%3Atag.leaks