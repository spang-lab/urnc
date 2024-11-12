import pytest
import urnc


@pytest.fixture(autouse=True)
def setup_logger():
    urnc.logger.setup_test_logger()
