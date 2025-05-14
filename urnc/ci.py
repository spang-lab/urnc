"""Functions to be used by CI pipelines"""

import os
import shutil
from datetime import datetime
from os.path import basename, exists, isdir, isfile, join
from pathlib import Path
from typing import Optional, Dict, Any, List

import dateutil
import dateutil.tz
import dateutil.parser
import git
import click
import urnc
from urnc.logger import critical, log, warn


def clone_student_repo(config: Dict[str, Any]) -> git.Repo:
    """
    Clones the student repository if it doesn't exist locally, or returns the existing local repository.
    If the 'student' key is not found in the 'git' section of the config, it initializes a new student repository.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        git.Repo: The cloned, existing, or newly initialized local git repository.

    Raises:
        Exception: If the 'student' key is not found in the 'git' section of the config and the initialization of a new repository fails.
        Exception: If the local repository exists but is not a git repository.
        Exception: If there is a mismatch between the remote URL and the local repository's URL.
    """
    base_path = config["base_path"]
    repo_url = config["git"]["student"]
    output_dir = config["git"]["output_dir"]
    if not repo_url:
        raise click.UsageError("No student repository git.student specified in config")

    stud_path = base_path.joinpath(output_dir)

    # Return existing repo if already available at local filesystem
    if stud_path.exists():
        log(f"Returning existing repo {stud_path}")
        try:
            stud_repo = git.Repo(stud_path)
        except Exception:
            critical(f"Folder '{stud_path}' exists but is not a git repo")
        if stud_repo.remote().url != repo_url:
            critical(
                f"Repo remote mismatch. Expected: {repo_url}. Observed: {stud_repo.remote().url}."
            )
        stud_repo.remote().pull()
        return stud_repo

    # Clone and return repo if not available locally
    log(f"Cloning student repo {repo_url} to {stud_path}")
    stud_repo = git.Repo.clone_from(url=repo_url, to_path=stud_path)
    urnc.git.set_commit_names(stud_repo)
    return stud_repo


def clear_repo(repo: git.Repo) -> None:
    path = repo.working_dir
    entries = os.listdir(path)
    for entry in entries:
        if entry == ".git":
            continue
        entry_path = join(path, entry)
        if isfile(entry_path):
            os.remove(entry_path)
        if isdir(entry_path):
            shutil.rmtree(entry_path)


def write_gitignore(main_gitignore: Optional[Path],
                    student_gitignore: Path,
                    config: Dict[str, Any]) -> None:
    """
    Writes a ``.gitignore`` file in the student repository.

    This function copies the ``.gitignore`` file from the main repository (if it exists) and appends additional patterns to exclude based on the configuration.

    Parameters:
        main_gitignore (Optional[str]): The path to the .gitignore file in the main repository. If None, no .gitignore file is copied.
        student_gitignore (str): The path to the .gitignore file in the student repository.
        config (Dict): The configuration dictionary. Can contain a ``git`` key with a ``exclude`` key, which should be a list of patterns to exclude. Each pattern can be a string or a dictionary with a ``pattern`` key and optional ``after`` and ``until`` keys specifying a date range, e.g.::

                git:
                    exclude:
                        - *.pyc
                        - /tutorials/*.*
                        - {pattern: '!tutorials/Tutorial_1.ipynb', after: '2023-10-25 9:30 CET'}
                        - {pattern: '!tutorials/Tutorial21.ipynb', after: '2023-10-25 9:30 CET'}
    """
    if main_gitignore and exists(main_gitignore):
        shutil.copy(main_gitignore, student_gitignore)

    exclude = config["git"]["exclude"]
    if not isinstance(exclude, list):
        critical("config.git.exclude must be a list")
    now = datetime.now(dateutil.tz.tzlocal())
    with open(student_gitignore, "a", newline="\n") as gitignore:
        gitignore.write("\n")
        for value in exclude:
            if isinstance(value, str):
                gitignore.write(f"{value}\n")
                continue
            if "after" in value:
                after_time = dateutil.parser.parse(value["after"])
                if now < after_time.astimezone(dateutil.tz.tzlocal()):
                    continue
            if "until" in value:
                until_time = dateutil.parser.parse(value["until"])
                if now > until_time.astimezone(dateutil.tz.tzlocal()):
                    continue
            gitignore.write(f"{value['pattern']}\n")


def update_index(repo: git.Repo) -> None:
    cached_files_str = repo.git.ls_files("-ci", "--exclude-standard")
    if cached_files_str != "":
        cached_files = cached_files_str.split("\n")
        log(f"Removing excluded files {cached_files}")
        repo.index.remove(cached_files, working_tree=False)
        repo.index.write()


def ci(config: Dict[str, Any]) -> None:
    """
    Performs a continuous integration run by:

    1. Cloning or pulling STUDENT_REPO as STUDENT_PATH
    2. Deleting all non-hidden files in STUDENT_PATH
    3. Copying all non-hidden files from ADMIN_PATH to STUDENT_PATH
    4. Converting all notebooks in STUDENT_PATH according to CONVERT_SETTINGS
    5. Updating STUDENT_PATH/.gitignore according to GIT_EXCLUDES
    6. Commiting and pushing the changes if COMMIT is True

    All configuration values mentioned above are taken from config:

    ADMIN_PATH       = config["base_path"]
    STUDENT_REPO     = config["git"]["student"]
    STUDENT_PATH     = config["git"]["output_dir"]
    GIT_EXCLUDES     = config["git"]["exclude"]
    CONVERT_SETTINGS = config["convert"]

    For a list of configuration values, see
    https://spang-lab.github.io/urnc/configuration.html

    Parameters:
        config: configuration dictionary as returned by `urnc.config.read()`

    Raises:
        Exception: If the repository is dirty and commit is True.
    """
    base_path = config["base_path"]
    repo = urnc.git.get_repo(base_path)
    if not repo:
        warn("Not in a git repository")

    # Make sure main repo is clean if we want to commit and push to student remote
    if config["ci"]["commit"] and repo and repo.is_dirty():
        raise click.UsageError("Repo is not clean. Commit your changes first.")

    # Clone and clear student repo. Then copy over files from main repo
    student_repo = clone_student_repo(config)
    student_path = Path(student_repo.working_dir)
    clear_repo(student_repo)

    def ignore_fn(dir: str, files: List[str]) -> List[str]:
        ignore_list = [".git"] if ".git" in files else []
        if Path(dir) == student_path.parent:
            log(f"Skipping copy of {student_path}")
            ignore_list.append(basename(student_path))
        return ignore_list

    shutil.copytree(base_path, student_path, ignore=ignore_fn, dirs_exist_ok=True)

    targets = config["convert"]["targets"]
    if not targets:
        targets = [
            {
                "type": "student",
                "path": "{nb.abspath}",
            }
        ]
    urnc.convert.convert(config, student_path, targets)

    log("Notebooks converted")
    # Update .gitignore and drop cached files
    log("Updating .gitignore from config")
    write_gitignore(
        main_gitignore=base_path.joinpath(".gitignore"),
        student_gitignore=student_path.joinpath(".gitignore"),
        config=config,
    )
    log("Dropping cached files...")
    update_index(student_repo)

    # Commit and push
    if config["ci"]["commit"]:
        log("Adding files and commiting")
        student_repo.git.add(all=True)
        student_repo.index.commit("urnc convert")
        log("Pushing student repo")
        student_repo.git.push()
        log("Done.")
    else:
        log("Skipping git commit and push")
        log("Done.")
