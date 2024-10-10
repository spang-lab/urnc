import re
from subprocess import run
import sys


def test_version_command():
    cmd = f"{sys.executable} -m urnc --version".split()
    proc = run(cmd, capture_output=True, encoding="utf-8")
    errors = []

    # Check results
    if proc.returncode != 0:
        errors.append(f"Returncode should be 0 but is: {proc.returncode}")
    if proc.stderr != "":
        errors.append(f"Stderr should be empty but is: {proc.stderr}")
    for error in errors:
        print(error)
    n_errors = len(
        errors
    )  # Store in extra var to get nicer pytest output in case of errors
    assert n_errors == 0
