import os
import pathlib
import tempfile

import git

import urnc


def test_init_with_default_args():
    path = urnc.init.init(name="Test Course")
    repo = git.Repo(path)
    config = urnc.config.read_config("test_course")
    admin_path = pathlib.Path(repo.git_dir).parent
    config = urnc.config.read_config(admin_path)
    # Check created files
    assert admin_path.exists()
    assert len(os.listdir(".")) == 1
    # Check local admin repo
    assert isinstance(repo, git.Repo)
    assert not repo.bare
    assert repo.remotes == []
    assert len(list(repo.iter_commits())) == 1
    # Check config
    assert config.get("name", "") == "Test Course"
    assert config.get("git", {}).get("student", "") == "Link to student repo"


def test_init_with_remote_urls():
    tmp_path = pathlib.Path(tempfile.mkdtemp())
    course_name = "Test Course"
    admin_path = tmp_path / "course"
    admin_url = "git@github.com:example-user/test-course.git"
    student_url = "git@github.com:example-user/test-course-public.git"
    path = urnc.init.init(course_name, admin_path, admin_url, student_url)
    repo = git.Repo(path)
    config = urnc.config.read_config(admin_path)
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
    course_name = "Test Course"
    admin_path = pathlib.Path("test-course-admin")
    admin_url = pathlib.Path("test-course-admin.git").absolute()
    student_url = pathlib.Path("test-course.git").absolute()
    path = urnc.init.init(course_name, admin_path, admin_url, student_url)
    repo = git.Repo(path)
    config = urnc.config.read_config(admin_path)
    # Check created files
    assert admin_path.exists()
    assert admin_url.exists()
    assert student_url.exists()
    assert len(os.listdir(".")) == 3
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
    urnc.util.release_locks(repo)
