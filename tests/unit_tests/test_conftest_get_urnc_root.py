from os.path import dirname, abspath, normpath
from os import chdir
from conftest import get_urnc_root

cfd = dirname(abspath(__file__))
urd = normpath(f"{cfd}/../..")


def test_get_urnc_root__from_urnc_root():
    assert get_urnc_root() == urd


def test_get_urnc_root__from_urnc_subdir():
    chdir(f"{urd}/tests")
    try:
        assert get_urnc_root() == urd
    finally:
        chdir(urd)


def test_get_urnc_root__from_outside_urnc_repo():
    chdir(f"{urd}/..")
    exception_raised = False
    try:
        get_urnc_root()
    except Exception as e:
        exception_raised = True
    finally:
        chdir(urd)
    assert exception_raised
