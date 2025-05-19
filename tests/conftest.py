import pytest
import urnc
import os

@pytest.fixture(autouse=True)
def change_to_temp_dir(tmp_path: pytest.TempPathFactory):
    old_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        yield
    finally:
        os.chdir(old_cwd)


@pytest.fixture(autouse=True)
def setup_logger():
    urnc.logger.setup_test_logger()
