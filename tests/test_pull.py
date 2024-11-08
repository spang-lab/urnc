from pathlib import Path
import git
import tempfile

import urnc


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
    git.Repo.init(remote_path, bare=True)
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
