import re
from subprocess import run
import sys

def test_version_command():
    cmd = f"{sys.executable} -m urnc --version".split()
    proc = run(cmd, capture_output=True, encoding="utf-8")
    errors = []
    semver = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$' # https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string

    # Check results
    if proc.returncode != 0:
        errors.append(f"Returncode should be 0 but is: {proc.returncode}")
    if proc.stderr != "":
        errors.append(f"Stderr should be empty but is: {proc.stderr}")
    if not re.match(semver, proc.stdout):
        errors.append(f"Version should be in semver format but is: {proc.stdout}")
    for error in errors:
        print(error)
    n_errors = len(errors) # Store in extra var to get nicer pytest output in case of errors
    assert n_errors == 0
