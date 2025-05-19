from pathlib import Path
from tempfile import mkdtemp

import os
import git

from urnc.config import read_config
from click.testing import CliRunner
from urnc.main import main  # or import your specific command

from urnc.init import init
from urnc.util import read_notebook


def test_init_with_default_args():
    repo = init(name="Test Course")
    config = read_config("test_course")
    admin_path = Path(repo.git_dir).parent
    config = read_config(admin_path)
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
    course_name = "Test Course"
    admin_path = Path("test-course-admin")
    admin_url = Path("test-course-admin.git")
    student_url = Path("test-course.git")
    repo = init(course_name, admin_path, admin_url, student_url)
    config = read_config(admin_path)

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

    repo.git.clear_cache() # (1)
    # (1) Required on Windows because gitPython is buggy and doesn't clean up open file handles.
    # For details see: https://github.com/gitpython-developers/GitPython/issues?q=label%3Atag.leaks


def test_init_full_cli(tmp_path: Path):
    print("tmp_path", tmp_path)
    runner = CliRunner()
    args = ["init", "My Course", "-p", "my_course", "-t", "full"]
    result = runner.invoke(main, args)
    assert result.exit_code == 0
    assert Path("my_course/images").is_dir()
    assert Path("my_course/lectures/week1").is_dir()
    assert Path("my_course/lectures/week1/lecture1.ipynb").is_file()
    assert Path("my_course/lectures/week1/lecture2.ipynb").is_file()
    assert Path("my_course/assignments").is_dir()
    assert Path("my_course/assignments/week1.ipynb").is_file()
    assert Path("my_course/config.yaml").is_file()
    assert Path("my_course/.git").is_dir()
    assert Path("my_course/.gitignore").is_file()
