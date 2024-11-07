import textwrap
import urnc.version as version
import click
import tempfile

from ruamel.yaml import YAML
from pathlib import Path
from traitlets.config import Config


def test_bump():
    assert version.bump("1.2.3", "show") is None
    assert version.bump("1.2.3", "patch") == "1.2.4"
    assert version.bump("1.2.3", "minor") == "1.3.0"
    assert version.bump("1.2.3", "major") == "2.0.0"
    assert version.bump("1.2.3-1", "prerelease") == "1.2.3-2"
    try:
        version.bump("1.2.3", "invalid")
    except Exception as e:
        assert isinstance(e, click.UsageError)


def test_version():
    with tempfile.TemporaryDirectory() as tmp:
        config = {
            "base_path": Path(tmp),
        }
        config_path = Path(tmp).joinpath("config.yaml")
        yaml = YAML(typ="rt")
        with open(config_path, "w", newline="\n") as f:
            yaml.dump({"version": "1.2.3"}, f)
        assert version.version_course(config, "show") == "1.2.3"

        assert version.version_course(config, "patch") == "1.2.4"
        with open(config_path, "r") as f:
            data = yaml.load(f)
            assert data["version"] == "1.2.4"


def test_version_self():
    file_content = textwrap.dedent(
        """
    [project]
    name = "urnc"
    version = "1.2.3"
    authors = [
        { name = "Michael Huttner", email = "michael@mhuttner.com" },
        { name = "Tobias Schmidt", email = "tobias.schmidt331@gmail.com" },
    ]
    """
    )
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp).joinpath("pyproject.toml")
        with open(config_path, "w", newline="\n") as f:
            f.write(file_content)

        assert version.read_pyproject_version(config_path) == "1.2.3"
        version.write_pyproject_version(config_path, "1.2.4")
        assert version.read_pyproject_version(config_path) == "1.2.4"
