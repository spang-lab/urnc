import tempfile
import textwrap
from pathlib import Path
from urnc.config import default_config, read


def test_config():
    config = default_config("/path/to/course")
    assert config["version"] is None
    assert config["base_path"] == "/path/to/course"
    assert config["convert"]["write_mode"] == "skip-existing"
    assert config["convert"]["targets"] == []


def test_yaml_file():
    file_content = textwrap.dedent(
        """
        version: "1.2.3"
        convert:
            write_mode: "overwrite"
            targets:
                - student
                - solution
            keywords:
                solution:
                    - solution
                skeleton:
                    - skeleton
                assignment:
                    - assignment
            tags:
                solution: "solution"
                skeleton: "skeleton"
                assignment: "assignment"
                assignment-start: "assignment-start"
                ignore: "ignore"
                no-execute: "no-execute"
        git:
            student: "git-url"
            output_dir: "out"
            exclude:
                - ".git"
        """
    ).strip()
    config = None
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp).joinpath("config.yaml")
        with open(config_path, "w", newline="\n") as f:
            f.write(file_content)
        config = read(config_path)
    assert config["version"] == "1.2.3"
    assert config["convert"]["write_mode"] == "overwrite"
    assert config["git"]["student"] == "git-url"
