"""Helper functions for unit/regression testing."""
import platform
from os import chmod
from os.path import isdir
import shutil
from stat import S_IWRITE

python = "python" if platform.system() == "Windows" else "python3"

def remove_readonly_attribute(func, path, _):
    "Helper function for rmtree. Clears the readonly bit and reattempts removal."
    chmod(path, S_IWRITE)
    func(path)

def rmtree(path):
    """Remove a directory tree, even if it is read-only."""
    if isdir(path):
        shutil.rmtree(path, onerror=remove_readonly_attribute)
    assert not isdir(path), f"Failed to remove {path}"
