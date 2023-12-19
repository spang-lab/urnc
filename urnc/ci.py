"""Functions to be used by CI pipelines"""

import os
import shutil
from datetime import datetime
from os.path import basename, dirname, exists, isdir, isfile, join, splitext
from pathlib import Path

import dateutil.parser
import git

import urnc
from urnc.logger import critical, log, setup_logger, warn
from urnc.util import (get_config_value, get_git_repo, read_config,
                       update_repo_config)


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
    main_repo = get_git_repo()
    main_path = Path(main_repo.working_dir)
    main_name = basename(main_path)
    stud_url = get_config_value(config, "git", "student")

    # Init and return new repo if no student repo is specified
    if (stud_url is None):
        stud_name = f"{main_name}-student"
        stud_path = main_path.parent.joinpath(stud_name)
        log(f"Property git.student not found in config. Initializing new student repo at {stud_path}")
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
            critical(f"Repo remote mismatch. Expected: {stud_url}. Observed: {stud_repo.remote().url}.")
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
        if (entry.startswith(".")):
            continue
        entry_path = join(path, entry)
        if isfile(entry_path):
            os.remove(entry_path)
        if isdir(entry_path):
            shutil.rmtree(entry_path)


def copy_files(repo, student_repo):
    path = repo.working_dir
    target_path = student_repo.working_dir
    entries = os.listdir(path)
    for entry in entries:
        if (entry.startswith(".")):
            continue
        entry_path = join(path, entry)
        copy_path = join(target_path, entry)
        if isfile(entry_path):
            shutil.copy2(entry_path, copy_path)
        if isdir(entry_path):
            shutil.copytree(entry_path, copy_path)


def write_gitignore(repo, student_repo, config):
    main_gitignore = join(repo.working_dir, ".gitignore")
    student_gitignore = join(student_repo.working_dir, ".gitignore")
    if (exists(main_gitignore)):
        shutil.copy(main_gitignore, student_gitignore)
    exclude = get_config_value(config, "git", "exclude", default=[])
    now = datetime.now()
    with open(student_gitignore, "a") as gitignore:
        for value in exclude:
            if isinstance(value, str):
                gitignore.write(f"{value}\n")
            else:
                if "after" in value:
                    if now < dateutil.parser.parse(value["after"]):
                        continue
                if "until" in value:
                    if now > dateutil.parser.parse(value["until"]):
                        continue
                gitignore.write(f"{value['pattern']}\n")


def update_index(repo):
    cached_files_str = repo.git.ls_files("-ci", "--exclude-standard")
    if (cached_files_str != ''):
        cached_files = cached_files_str.split("\n")
        log(f"Removing excluded files {cached_files}")
        repo.index.remove(cached_files, working_tree=False)
        repo.index.write()


def ci(commit=True):
    setup_logger(use_file=False)
    config = read_config()
    repo = get_git_repo()
    if (repo.is_dirty() and commit):
        raise Exception(f"Repo is not clean. Commit your changes.")

    # Clone and clear student repo. Then copy over files from course repo.
    student_repo = clone_student_repo(config)
    clear_repo(student_repo)
    copy_files(repo, student_repo)

    # Convert notebooks
    log("Converting files")
    urnc.convert.convert(input=repo.working_dir,
                         output=student_repo.working_dir,
                         force=True,
                         dry_run=False)
    log("Notebooks converted")

    # Update .gitignore and drop cached files
    log("Updating .gitignore from config")
    write_gitignore(repo, student_repo, config)
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
