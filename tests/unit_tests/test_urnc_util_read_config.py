import urnc
import pytest
import click

def test_read_config_for_valid_config():
    config_expected = {
        "name": "Minimal Course",
        "version": "1.0.0",
        "description": "Minimal Course for testing URNC's functionality",
        "ci": {
            "solution": "{nb.reldirpath}/solutions/{nb.name}"
        }
    }
    config_observed = urnc.util.read_config(course_root = "tests/inputs/minimal-course")
    assert config_observed == config_expected

def test_read_config_for_broken_config():
    # Idea: open `tests/inputs/broken-course/config.yaml` for writing so it cannot be opened for reading by `read_config()`
    with open("tests/inputs/broken-course/config.yaml", "w") as f:
        with pytest.raises(click.FileError):
            urnc.util.read_config(course_root = "tests/inputs/broken-course")

def test_read_config_for_missing_config():
    with pytest.raises(click.UsageError):
        urnc.util.read_config(course_root = "tests")
