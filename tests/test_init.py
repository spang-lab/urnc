import tempfile
from pathlib import Path
import urnc


def test_init():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        config = urnc.config.default_config(path)
        urnc.init.init(config, "test_course")
        assert (path / "test_course").exists()
        assert (path / "test_course" / "config.yaml").is_file()
        assert (path / "test_course" / "example.ipynb").is_file()
        assert path / "test_course" / ".gitignore"
