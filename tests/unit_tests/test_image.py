from pathlib import Path
import nbformat
import tempfile

from traitlets.config import Config
from urnc.preprocessor import util
import urnc.preprocessor.image as image


def test_nx_image():
    nb = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell("![](./invalid/path/to/image.png)"),
            nbformat.v4.new_markdown_cell('<img src="./invalid/path/to/image.png">'),
        ]
    )
    config = Config()
    config.base_path = tempfile.TemporaryDirectory().name
    config.ImageChecker.invalid_tag = "invalid"
    preprocessor = image.ImageChecker(config=config)
    tagged, _ = preprocessor.preprocess(nb, {"path": "irrelevant"})
    assert util.has_tag(tagged.cells[0], "invalid")
    assert util.has_tag(tagged.cells[1], "invalid")


def test_valid():
    with tempfile.TemporaryDirectory() as tmp:
        img_folder = Path(tmp).joinpath("images")
        img_folder.mkdir()

        img_path = img_folder.joinpath("image.png")
        img_path.touch()

        nb_path = Path(tmp).joinpath("notebook.ipynb")

        rel_path = img_path.relative_to(Path(tmp))

        config = Config()
        config.ImageChecker.invalid_tag = "invalid"
        config.ImageChecker.base_path = tmp

        nb = nbformat.v4.new_notebook(
            cells=[
                nbformat.v4.new_markdown_cell(f"![]({rel_path})"),
                nbformat.v4.new_markdown_cell(f'<img src="{rel_path}">'),
            ]
        )
        preprocessor = image.ImageChecker(config=config)
        tagged, _ = preprocessor.preprocess(nb, {"path": nb_path})
        assert util.has_tag(tagged.cells[0], "invalid") is False
        assert util.has_tag(tagged.cells[1], "invalid") is False


def test_autofix():
    with tempfile.TemporaryDirectory() as tmp:
        img_folder = Path(tmp).joinpath("images")
        img_folder.mkdir()

        img_path = img_folder.joinpath("image.png")
        img_path.touch()

        bad_folder = Path(tmp).joinpath("invalid_folder")
        bad_path = bad_folder.joinpath("image.png")

        nb_path = Path(tmp).joinpath("notebook.ipynb")

        rel_path = bad_path.relative_to(Path(tmp))

        config = Config()
        config.ImageChecker.invalid_tag = "invalid"
        config.ImageChecker.base_path = tmp
        config.ImageChecker.autofix = True

        nb = nbformat.v4.new_notebook(
            cells=[
                nbformat.v4.new_markdown_cell(f"![]({rel_path})"),
                nbformat.v4.new_markdown_cell(f'<img src="{rel_path}">'),
            ]
        )
        preprocessor = image.ImageChecker(config=config)
        tagged, _ = preprocessor.preprocess(nb, {"path": nb_path})
        assert util.has_tag(tagged.cells[0], "invalid")
        assert util.has_tag(tagged.cells[1], "invalid")
        tagged2, _ = preprocessor.preprocess(tagged, {"path": nb_path})
        print(tagged2.cells[0].source)
        assert util.has_tag(tagged2.cells[0], "invalid") is False
        assert util.has_tag(tagged2.cells[1], "invalid") is False
