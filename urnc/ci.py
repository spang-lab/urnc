"""Functions to be used by CI pipelines"""

import os
import shutil
from datetime import datetime
from os.path import basename, dirname, exists, isdir, isfile, join, splitext
from pathlib import Path
from typing import Optional, Dict

import dateutil.parser
import git

import urnc
from urnc.logger import critical, log, setup_logger, warn
from urnc.util import get_config_string, get_config_value, update_repo_config


def clone_student_repo(config: dict) -> git.Repo:
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

    # Get info about main repo
    main_path = urnc.util.get_course_root()
    main_name = basename(main_path)
    stud_url = get_config_string(config, "git", "student")

    # Init and return new repo if no student repo is specified
    if stud_url is None:
        stud_name = f"{main_name}-student"
        stud_path = main_path.parent.joinpath(stud_name)
        log(
            f"Property git.student not found in config. Initializing new student repo at {stud_path}"
        )
        stud_repo = git.Repo.init(stud_path)
        return stud_repo

    # Collect info about student repo if specified in config.yaml
    stud_name = splitext(basename(stud_url))[0]
    if stud_name == main_name:
        stud_name = f"{main_name}-student"
    stud_path = main_path.parent.joinpath(stud_name)

    # Return existing repo if already available at local filesystem
    if stud_path.exists():
        log(f"Returning existing repo {stud_path}")
        try:
            stud_repo = git.Repo(stud_path)
        except Exception:
            critical(f"Folder '{stud_path}' exists but is not a git repo")
        if stud_repo.remote().url != stud_url:
            critical(
                f"Repo remote mismatch. Expected: {stud_url}. Observed: {stud_repo.remote().url}."
            )
        stud_repo.remote().pull()
        return stud_repo

    # Clone and return repo if not available locally
    log(f"Cloning student repo {stud_url} to {stud_path}")
    stud_repo = git.Repo.clone_from(url=stud_url, to_path=stud_path)
    update_repo_config(stud_repo)
    return stud_repo


def clear_repo(repo):
    path = repo.working_dir
    entries = os.listdir(path)
    for entry in entries:
        if entry.startswith("."):
            continue
        entry_path = join(path, entry)
        if isfile(entry_path):
            os.remove(entry_path)
        if isdir(entry_path):
            shutil.rmtree(entry_path)


def copy_files(path, target_path):
    entries = os.listdir(path)
    for entry in entries:
        if entry.startswith("."):
            continue
        entry_path = join(path, entry)
        copy_path = join(target_path, entry)
        if isfile(entry_path):
            shutil.copy2(entry_path, copy_path)
        if isdir(entry_path):
            shutil.copytree(entry_path, copy_path)


def write_gitignore(
    main_gitignore: Optional[str], student_gitignore: str, config: Dict
) -> None:
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
    exclude = get_config_value(config, "git", "exclude", default=[])
    if not isinstance(exclude, list):
        critical("config.git.exclude must be a list")
    now = datetime.now()
    with open(student_gitignore, "a", newline="\n") as gitignore:
        gitignore.write("\n")
        for value in exclude:
            if isinstance(value, str):
                gitignore.write(f"{value}\n")
                continue
            if "after" in value and now < dateutil.parser.parse(value["after"]):
                continue
            if "until" in value and now > dateutil.parser.parse(value["until"]):
                continue
            gitignore.write(f"{value['pattern']}\n")


def update_index(repo):
    cached_files_str = repo.git.ls_files("-ci", "--exclude-standard")
    if cached_files_str != "":
        cached_files = cached_files_str.split("\n")
        log(f"Removing excluded files {cached_files}")
        repo.index.remove(cached_files, working_tree=False)
        repo.index.write()


def ci(commit=True):
    """
    Perform a continuous integration run on a student repository.

    This function

    1. Clones the student repository
    2. Clears it
    3. Copies over all files from the course repository
    4. Converts the notebooks
    5. Updates the .gitignore file according to the `git.exclude` setting from the `config.yaml`
    6. Commits and pushes the changes if `commit` is True

    Parameters:
        commit (bool): commit and push updates?

    Raises:
        Exception: If the repository is dirty and commit is True, an exception is raised.

    Examples:
        >>> ci(commit=True)   # This will commit and push the changes
        >>> ci(commit=False)  # This will not commit or push the changes
    """
    setup_logger(use_file=False)
    course_root = urnc.util.get_course_root()
    course_config = urnc.util.read_config()

    # Make sure main repo is clean if we want to commit and push to student remote
    if commit:
        course_repo = urnc.util.get_course_repo()
        if course_repo.is_dirty():
            raise Exception("Repo is not clean. Commit your changes first.")

    # Clone and clear student repo. Then copy over files from main repo
    student_repo = clone_student_repo(course_config)
    student_root = Path(student_repo.working_dir)
    clear_repo(student_repo)
    copy_files(course_root, student_root)

    # Convert notebooks
    solution_relpath = get_config_string(course_config, "ci", "solution", default=None)
    solution_pattern = (
        student_root.joinpath(solution_relpath) if solution_relpath else None
    )
    with urnc.util.chdir(student_root):
        # Paths printed as info messages by urnc.convert.convert are relative to the current working directory, so we change the working directory to the student repo root in order to get the shorter paths in the log messages.
        urnc.convert.convert(
            input=student_root,
            output=student_root,
            solution=solution_pattern,
            force=True,
            dry_run=False,
        )
    log("Notebooks converted")

    # Update .gitignore and drop cached files
    log("Updating .gitignore from config")
    write_gitignore(
        main_gitignore=course_root.joinpath(".gitignore"),
        student_gitignore=student_root.joinpath(".gitignore"),
        config=course_config,
    )
    log("Dropping cached files...")
    update_index(student_repo)

    # Commit and push
    if commit:
        log("Adding files and commiting")
        student_repo.git.add(all=True)
        student_repo.index.commit("urnc convert")
        log("Pushing student repo")
        student_repo.git.push()
        log("Done.")
    else:
        log("Skipping git commit and push")
        log("Done.")
