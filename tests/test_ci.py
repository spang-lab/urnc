from pathlib import Path
import git
import tempfile

import nbformat
import urnc
from urnc.config import WriteMode
import urnc.preprocessor.util as util


def test_ci():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name)
    repo_path = path / "repo"
    d_config = urnc.config.default_config(path)
    repo = urnc.init.init(d_config, "repo")

    remote_path = path / "remote.git"
    remote_path.mkdir()
    git.Repo.init(remote_path, bare=True, initial_branch="main")
    origin = repo.create_remote("origin", str(remote_path))
    origin.push(refspec="main:main")

    student_remote = path / "student.git"
    student_remote.mkdir()
    git.Repo.init(student_remote, bare=True, initial_branch="main")

    config = urnc.config.read(repo_path)
    config["git"]["student"] = str(student_remote)
    config["git"]["output_dir"] = "out"
    config["convert"]["write_mode"] = WriteMode.OVERWRITE
    config["ci"]["commit"] = True
    urnc.ci.ci(config)

    student_repo_path = path / "student"
    urnc.pull.pull(str(student_remote), str(student_repo_path), "main", 1)

    assert (student_repo_path / "example.ipynb").is_file()
    assert not (student_repo_path / "config.yaml").exists()

    nb = nbformat.read(str(student_repo_path / "example.ipynb"), as_version=4)
    cells = nb["cells"]
    print(cells)
    assert util.has_tag(cells[2], "assignment")
    assert util.has_tag(cells[2], "assignment-start")
    assert util.has_tag(cells[3], "assignment")
    tmp.cleanup()
