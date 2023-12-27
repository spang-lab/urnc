import re
from os.path import exists
from pathlib import Path
from subprocess import run

import pytest
from git import Repo

from conftest import python


@pytest.mark.slow
def test_student_command_in_data_science_repo():
    print("Running `urnc student` in data_science repo. Takes approx. 30 secs.")

    # Constants
    repo_path = Path("tests/courses/data-science")
    repo_url = "git@git.uni-regensburg.de:fids/data-science.git"
    repo_hash = "d048dae38563a96c746024c42a0de446b8e92581"  # 2023-12-17
    out_path = Path("tests/courses/data-science-output/stdout.txt")
    err_path = Path("tests/courses/data-science-output/stderr.txt")
    out_exp = Path("tests/courses/data-science-output/stdout_expected.txt")
    cmd = f"{python} -m urnc student".split()

    # Clone repo
    repo = Repo.clone_from(repo_url, repo_path) if not repo_path.exists() else Repo(repo_path)
    repo.git.checkout(repo_hash)
    repo.git.reset("--hard", repo_hash)

    # Run urnc student
    with open(out_path, "w") as out_hndl, open(err_path, "w") as err_hndl:
        proc = run(cmd, cwd=repo_path, stdout=out_hndl, stderr=err_hndl, encoding="utf-8")

    # Remove ANSI escape sequences, platform dependent path parts and first line from output
    out_text = out_path.read_text()
    out_text = re.sub(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]', '', out_text)
    out_text = re.sub(str(repo_path.absolute().parent).replace("\\", "\\\\"), '', out_text)
    out_text = "\n".join(out_text.splitlines()[1:]) # remove first line
    out_path.write_text(out_text)
    err_text = err_path.read_text()

    # Check results
    errors = []
    if proc.returncode != 0:
        errors.append(f"Returncode should be 0 but is {proc.returncode}")
    if err_text != "":
        errors.append(f"Stderr ({err_path.absolute()}) has length {len(err_text)}")
    if out_text != out_exp.read_text():
        errors.append(f"Observed stdout ({out_path.absolute()}) differs from expected stdout ({out_exp.absolute()})")
    for error in errors:
        print(error)
    n_errors = len(errors) # Store in extra var to get nicer pytest output in case of errors
    assert n_errors == 0


@pytest.mark.slow
def test_student_command_in_developer_skills_repo():
    print("Running `urnc student` in developer_skills repo.")

    # Constants
    repo_path = Path("tests/courses/developer-skills")
    repo_url = "git@git.uni-regensburg.de:fids/developer-skills.git"
    repo_hash = "e8a5da315bedadf696824b37c177ad706d5d4563"  # 2023-12-14
    out_path = Path("tests/courses/developer-skills-output/stdout.txt")
    err_path = Path("tests/courses/developer-skills-output/stderr.txt")
    out_exp = Path("tests/courses/developer-skills-output/stdout_expected.txt")
    cmd = f"{python} -m urnc student".split()

    # Clone repo
    repo = Repo.clone_from(repo_url, repo_path) if not repo_path.exists() else Repo(repo_path)
    repo.git.checkout(repo_hash)
    repo.git.reset("--hard", repo_hash)

    # Run urnc student
    with open(out_path, "w") as out_hndl, open(err_path, "w") as err_hndl:
        proc = run(cmd, cwd=repo_path, stdout=out_hndl, stderr=err_hndl, encoding="utf-8")

    # Remove ANSI escape sequences, platform dependent path parts and first line from output
    out_text = out_path.read_text()
    out_text = re.sub(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]', '', out_text)
    out_text = re.sub(str(repo_path.absolute().parent).replace("\\", "\\\\"), '', out_text)
    out_text = "\n".join(out_text.splitlines()[1:]) # remove first line
    out_path.write_text(out_text)
    err_text = err_path.read_text()

    # Check results
    errors = []
    if proc.returncode != 0:
        errors.append(f"Returncode should be 0 but is {proc.returncode}")
    if err_text != "":
        errors.append(f"Stderr ({err_path.absolute()}) has length {len(err_text)}")
    if out_text != out_exp.read_text():
        errors.append(f"Observed stdout ({out_path.absolute()}) differs from expected stdout ({out_exp.absolute()})")
    for error in errors:
        print(error)
    n_errors = len(errors) # Store in extra var to get nicer pytest output in case of errors
    assert n_errors == 0
