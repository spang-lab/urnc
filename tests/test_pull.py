from pathlib import Path
import git
import tempfile
import urnc


def test_pull():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name)
    config = urnc.config.default_config(path)
    repo = urnc.init.init(config, "test_course")

    remote_path = path.joinpath("remote.git")
    remote_path.mkdir()
    git.Repo.init(remote_path, bare=True)

    origin = repo.create_remote("origin", str(remote_path))
    origin.push(refspec="main:main")

    pull_path = path.joinpath("test_pulled")
    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert (path / "test_pulled").exists()
    assert (path / "test_pulled" / "config.yaml").is_file()
    nb_path = path / "test_pulled" / "example.ipynb"
    assert nb_path.is_file()
    nb_path.unlink()

    urnc.pull.pull(str(remote_path), str(pull_path), "main", 1)
    assert nb_path.is_file()

    tmp.cleanup()
