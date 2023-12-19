"""Functions to be used by CI pipelines"""

import os
import shutil
from datetime import datetime

import dateutil.parser
import git

import urnc


def clone_student_repo(config):
    url = urnc.util.get_config_value(config, "git", "student", required=True)
    assert (url is not None)
    repo_name_git = os.path.basename(url)
    repo_name, _ = os.path.splitext(repo_name_git)
    folder_name = f"{repo_name}-student"
    base_path = os.path.dirname(os.getcwd())
    repo_path = os.path.join(base_path, folder_name)
    if os.path.exists(repo_path):
        try:
            repo = git.Repo(repo_path)
            repo_url = repo.remote().url
            if (repo_url != url):
                return urnc.logger.critical(f"Repo remote mismatch {repo_url}!={url}")
            urnc.logger.log(f"Returning existing repo {repo_path}")
            return repo
        except Exception:
            return urnc.logger.critical(f"{repo_path} exists but is not a git repo")
    urnc.logger.log(f"Cloning student repo {url} to {repo_path}")
    repo = git.Repo.clone_from(url, repo_path)
    urnc.util.update_repo_config(repo)
    return repo


def clear_repo(repo):
    path = repo.working_dir
    entries = os.listdir(path)
    for entry in entries:
        if (entry.startswith(".")):
            continue
        entry_path = os.path.join(path, entry)
        if os.path.isfile(entry_path):
            os.remove(entry_path)
        if os.path.isdir(entry_path):
            shutil.rmtree(entry_path)


def copy_files(repo, student_repo):
    path = repo.working_dir
    target_path = student_repo.working_dir
    entries = os.listdir(path)
    for entry in entries:
        if (entry.startswith(".")):
            continue
        entry_path = os.path.join(path, entry)
        copy_path = os.path.join(target_path, entry)
        if os.path.isfile(entry_path):
            shutil.copy2(entry_path, copy_path)
        if os.path.isdir(entry_path):
            shutil.copytree(entry_path, copy_path)


def write_gitignore(repo, student_repo, config):
    main_gitignore = os.path.join(repo.working_dir, ".gitignore")
    student_gitignore = os.path.join(student_repo.working_dir, ".gitignore")
    if (os.path.exists(main_gitignore)):
        shutil.copy(main_gitignore, student_gitignore)
    exclude = urnc.util.get_config_value(config, "git", "exclude", default=[])
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
        urnc.logger.log(f"Removing excluded files {cached_files}")
        repo.index.remove(cached_files, working_tree=False)
        repo.index.write()


def ci(commit=True):
    urnc.logger.setup_logger(use_file=False)
    config = urnc.util.read_config()
    repo = urnc.util.get_git_repo()
    if (repo.is_dirty() and commit):
        raise Exception(f"Repo is not clean. Commit your changes.")

    # Clone and clear student repo. Then copy over files from course repo.
    student_repo = clone_student_repo(config)
    clear_repo(student_repo)
    copy_files(repo, student_repo)

    # Convert notebooks
    urnc.logger.log("Converting files")
    urnc.convert.convert(input=repo.working_dir,
                         output=student_repo.working_dir,
                         force=True,
                         dry_run=False)
    urnc.logger.log("Notebooks converted")

    # Update .gitignore and drop cached files
    urnc.logger.log("Updating .gitignore from config")
    write_gitignore(repo, student_repo, config)
    urnc.logger.log("Dropping cached files...")
    update_index(student_repo)

    # Commit and push
    if commit:
        urnc.logger.log("Adding files and commiting")
        student_repo.git.add(all=True)
        student_repo.index.commit("urnc convert")
        urnc.logger.log("Pushing student repo")
        student_repo.git.push()
        urnc.logger.log("Done.")
    else:
        urnc.logger.log("Skipping git commit and push")
        urnc.logger.log("Done.")
