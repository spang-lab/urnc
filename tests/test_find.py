from pathlib import Path
import tempfile
import urnc


def test_find_notebooks():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name)

    notebooks = urnc.convert.find_notebooks(path, None)
    assert notebooks == []

    (path / "example.ipynb").touch()
    (path / "folder").mkdir()
    (path / "folder" / "example2.ipynb").touch()
    notebooks = urnc.convert.find_notebooks(path, None)
    assert notebooks == [path / "example.ipynb", path / "folder" / "example2.ipynb"]

    assert 1 == 1
    tmp.cleanup()


def test_ignore_output_path():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name)

    (path / "example.ipynb").touch()
    output_path = path / "out"
    output_path.mkdir()
    (output_path / "example.ipynb").touch()

    notebooks = urnc.convert.find_notebooks(path, output_path)
    assert notebooks == [path / "example.ipynb"]

    assert 1 == 1
    tmp.cleanup()


def test_ignore_pattern():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name)

    p1 = path / "example.ipynb"
    p2 = path / "ignore_this.ipynb"
    p3 = path / "ignore_this_too.ipynb"
    folder = path / "folder"
    p4 = folder / "ignore_this_too.ipynb"
    p5 = folder / "example.ipynb"
    folder.mkdir()
    p1.touch()
    p2.touch()
    p3.touch()
    p4.touch()
    p5.touch()

    notebooks = urnc.convert.find_notebooks(path, None)
    assert notebooks.sort() == [p1, p2, p3, p4, p5].sort()

    notebooks = urnc.convert.filter_notebooks(notebooks, ["ignore*.ipynb"])
    assert notebooks.sort() == [p1, p5].sort()
    tmp.cleanup()
