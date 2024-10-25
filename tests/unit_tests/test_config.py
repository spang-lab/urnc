from urnc.config import default_config


def test_config():
    config = default_config("/path/to/course")
    assert config["version"] is None
    assert config["base_path"] == "/path/to/course"
    assert config["convert"]["write_mode"] == "skip-existing"
    assert config["convert"]["targets"] == []
