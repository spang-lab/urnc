import urnc
import pytest
import click

def test_read_config_for_valid_config():
    config_expected = {
        "name": "Minimal Course",
        "version": "1.0.0",
        "description": "Minimal Course for testing URNC's functionality",
        "convert": {
            "solution": "solutions/{notebook.name}"
        }
    }
    config_observed = urnc.util.read_config(course_root = "tests/courses/minimal")
    assert config_observed == config_expected

def test_read_config_for_broken_config():
    # Idea: open `tests/courses/broken/config.yaml` for writing so it cannot
    # be opened for reading by `read_config()`
    with open("tests/courses/broken/config.yaml", "w") as f:
        with pytest.raises(click.FileError):
            urnc.util.read_config(course_root = "tests/courses/broken")

def test_read_config_for_missing_config():
    with pytest.raises(click.UsageError):
        urnc.util.read_config(course_root = "tests")
