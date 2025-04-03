from pathlib import Path
import git
import tempfile

import urnc


def ls(path: Path):
    return [x.name for x in path.glob("*")]

def update_remote(repo: git.Repo):
    repo.git.add(all=True)
    repo.index.commit("update")
    origin = repo.remote()
    origin.push(refspec="main:main")


def test_pull():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name)

    # init repo
    repo_path = path / "repo"
    config = urnc.config.default_config(path)
    repo = urnc.init.init(config, "repo")

    # init remote
    remote_path = path / "remote.git"
    remote_path.mkdir()
    git.Repo.init(remote_path, bare=True, initial_branch="main")
    origin = repo.create_remote("origin", str(remote_path))
    origin.push(refspec="main:main")

    # test pull clones the repo
    pull_path = path / "pulled"
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert pull_path.is_dir()
    assert (pull_path / "config.yaml").is_file()
    assert (pull_path / "example.ipynb").is_file()

    # Test that locally deleted files are restored
    (pull_path / "example.ipynb").unlink()
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert (pull_path / "example.ipynb").is_file()

    # test the pull of new files
    (repo_path / "new_file.txt").write_text("line 1\nline 2\nline 3\nline 4\n")
    update_remote(repo)
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert (pull_path / "new_file.txt").is_file()

    # test merge of changed remote content
    lines = (repo_path / "new_file.txt").read_text().split("\n")
    lines[1] = "new line 2"
    (repo_path / "new_file.txt").write_text("\n".join(lines))
    update_remote(repo)
    with open(pull_path / "new_file.txt", "a") as f:
        f.write("line 5\n")
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert (
        pull_path / "new_file.txt"
    ).read_text() == "line 1\nnew line 2\nline 3\nline 4\nline 5\n"

    # test a merge conflict
    (repo_path / "conflict.txt").write_text("remote text")
    update_remote(repo)
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    (pull_path / "conflict.txt").write_text("local text")
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert (pull_path / "conflict.txt").read_text() == "local text"

    # test a modify/delete conflict
    (repo_path / "new_file.txt").unlink()
    update_remote(repo)
    (pull_path / "new_file.txt").write_text("Modified")
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert (pull_path / "new_file.txt").is_file()
    assert (pull_path / "new_file.txt").read_text() == "Modified"

    # test a file name conflict
    (repo_path / "collision.txt").write_text("remote file")
    update_remote(repo)
    (pull_path / "collision.txt").write_text("local file")
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert (pull_path / "collision.txt").read_text() == "remote file"

    renamed = pull_path.glob("collision_*.txt")
    assert len(list(renamed)) == 1

    tmp.cleanup()


def test_pull_delete_restore():

    tmp = tempfile.TemporaryDirectory()
    tmp_path = Path(tmp.name)
    remote_repo_path  = tmp_path / "remote.git"
    ci_repo_path      = tmp_path / "ci_repo" # e.g./tmp/tmpqu7ilrgr/ci_repo
    student_repo_path = tmp_path / "student_repo"
    print("Test paths:")
    print("remote_repo_path:", remote_repo_path)
    print("ci_repo_path:", ci_repo_path)
    print("student_repo_path:", student_repo_path)

    print("Initalizing remote repo")
    remote_repo_path.mkdir()
    git.Repo.init(remote_repo_path, bare=True, initial_branch="main")

    print("Init ci_repo (local clone for simulating changes pushed by CI)")
    ci_config = urnc.config.default_config(tmp_path)
    ci_repo = urnc.init.init(ci_config, "ci_repo") # creates: .git .gitignore config.yaml example.ipynb
    ci_repo.create_remote("origin", str(remote_repo_path))
    update_remote(ci_repo)

    print("Init student_repo (local clone obtained from urnc pull, as done in student sandboxes)")
    urnc.pull.pull(str(remote_repo_path), str(student_repo_path), "main", 1)
    student_repo = git.Repo(str(student_repo_path))

    print("Let urnc ci push two new files")
    (ci_repo_path / "tmp1.txt").write_text("tmp1")
    (ci_repo_path / "tmp2.txt").write_text("tmp2")
    update_remote(ci_repo)

    print("Let urnc pull these files")
    urnc.pull.pull(str(remote_repo_path), str(student_repo_path), "main", 1)

    student_files = ls(student_repo_path)
    assert "tmp1.txt" in student_files
    assert "tmp2.txt" in student_files

    print("Let student modify file one")
    (student_repo_path / "tmp1.txt").write_text("tmp1-modified")

    print("Let urnc ci delete all two files")
    ci_repo.git.clear_cache() # (1)
    (ci_repo_path / "tmp1.txt").unlink()
    (ci_repo_path / "tmp2.txt").unlink()
    update_remote(ci_repo)

    print("Let student pull the changes (this should lead to a MODIFY/DELETE conflict)")
    urnc.pull.pull(str(remote_repo_path), str(student_repo_path), "main", 1)
    git_log = student_repo.git.execute(["git", "log", "--oneline"])
    git_diff = student_repo.git.execute(["git", "diff", "--name-status", "HEAD~1", "HEAD"])
    student_files = ls(student_repo_path)
    tmp1_content = open(student_repo_path / "tmp1.txt", "r").read()
    print("git log --online:", git_log, sep = "\n")
    print("git diff --name-status HEAD~1 HEAD:", git_diff, sep = "\n")
    assert "Resolve CONFLICT (modify/delete)" in git_log
    assert "tmp1.txt" in student_files
    assert "tmp2.txt" not in student_files
    assert tmp1_content == "tmp1-modified"

    print("Let urnc ci restore both files")
    (ci_repo_path / "tmp1.txt").write_text("tmp1")
    (ci_repo_path / "tmp2.txt").write_text("tmp2")
    update_remote(ci_repo)

    print("Let student pull the changes (this should restore file two)")
    urnc.pull.pull(str(remote_repo_path), str(student_repo), "main", 1)
    student_files = ls(student_repo_path)
    assert "tmp1.txt" in student_files
    assert "tmp2.txt" in student_files
    tmp1_content = open(student_repo_path / "tmp1.txt", "r").read()
    tmp2_content = open(student_repo_path / "tmp2.txt", "r").read()
    assert tmp1_content == "tmp1-modified"
    assert tmp2_content == "tmp2"

    student_repo.git.clear_cache() # (1)
    ci_repo.git.clear_cache() # (1)
    del student_repo # (1)
    del ci_repo # (1)
    # (1) Required or Windows won't allow deletion of tmp at the end of the
    # test, because git processes are still running within that folder.
    # Details: https://github.com/gitpython-developers/GitPython/issues/546#issuecomment-256657166

    tmp.cleanup()
