"""Fetch and merge the student repo"""

import os
import git
import datetime

import urnc.util as util

import urnc.logger as log


def get_upstream_changes(repo):
    branch_name = repo.active_branch
    changes = repo.git.diff(f"..origin/{branch_name}", "--name-status").split("\n")
    return changes


def get_upstream_deleted(repo):
    changes = get_upstream_changes(repo)
    files = []
    for change in changes:
        parts = change.split("\t", 1)
        if len(parts) != 2:
            continue
        [ctype, file] = change.split("\t", 1)
        if ctype == "D":
            files.append(file)
    return files


def get_upstream_added(repo):
    changes = get_upstream_changes(repo)
    files = []
    for change in changes:
        parts = change.split("\t", 1)
        if len(parts) != 2:
            continue
        [ctype, file] = parts
        if ctype == "A":
            files.append(file)
    return files


def reset_deleted_files(repo):
    branch = repo.active_branch
    deleted_files = repo.git.ls_files("--deleted").split("\n")
    deleted_upstream = get_upstream_deleted(repo)
    for filename in deleted_files:
        if not filename:
            continue
        if filename in deleted_upstream:
            repo.git.checkout("HEAD", "--", filename)
        else:
            log.dbg(f"Restoring deleted file {filename}")
            repo.git.checkout(f"origin/{branch}", "--", filename)


def rename_file_with_timestamp(path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    (folder, filename) = os.path.split(path)
    (basename, ext) = os.path.splitext(filename)
    new_filename = f"{basename}_{timestamp}{ext}"
    new_path = os.path.join(folder, new_filename)
    log.warn(
        f"Renaming {path} to {new_path}, to avoid merge conflict with local untracked files."
    )
    os.rename(path, new_path)


def rename_local_untracked(repo):
    added_files = get_upstream_added(repo)
    for filename in added_files:
        if not filename:
            continue
        path = os.path.join(repo.working_dir, filename)
        if os.path.exists(path):
            rename_file_with_timestamp(path)


def merge(repo):
    branch = repo.active_branch
    remote_branch = f"origin/{branch}"
    try:
        repo.git.merge("-Xours", remote_branch)
    except git.GitCommandError as err:
        if "CONFLICT (modify/delete)" in str(err):
            log.warn(
                "Found a CONFLICT (modify/delete). Keeping the local file by commiting."
            )
            repo.git.commit("-am", "Resolve CONFLICT (modify/delete)", "--allow-empty")
            return
        log.error("!!!THIS SHOULD NOT HAPPEN!!!")
        log.error("Failed to merge. Error:")
        log.error(err)
        return


def get_repo(git_url, output, branch, depth):
    if not git_url:
        try:
            repo = git.Repo(os.getcwd(), search_parent_directories=True)
            return repo
        except Exception:
            log.error("Failed to pull: no git_url given and not in a git repo")
            return
    folder_name = output
    if not output:
        folder_name = util.git_folder_name(git_url)
    if not os.path.exists(folder_name):
        log.log(f"{folder_name} does not exists. Cloning repo {git_url}")
        try:
            git.Repo.clone_from(git_url, folder_name, branch=branch, depth=depth)
            log.log("Cloned successfully.")
            return None
        except Exception as err:
            log.error("Failed to clone repo. Error:")
            log.error(err)
            return None
    try:
        repo = git.Repo(folder_name)
        if git_url != repo.remote().url:
            log.error(
                f"Remote url {repo.remote().url} of folder {folder_name} does not match {git_url}"
            )
            return None
        return repo
    except Exception:
        log.error(f"Failed to pull: {folder_name} exists but is not a git repo")
        return None


def pull(git_url, output, branch, depth):
    """
    Pull (or clone) a remote git repository and try to automatically merge local changes.
    This is essentially a wrapper around git pull and git merge -Xours.

    Args:
        git_url (str): The URL of the git repository to pull.
        output (str): The name of the output folder.
        branch (str): The branch to pull.
        depth (int): The depth for git fetch.

    Returns:
        None

    Raises:
        Does not raise any exceptions, but logs errors and warnings.
        This is required because this function may be called from a jupyter postStart hook,
        and exception would prevent the notebook from starting.
    """
    repo = get_repo(git_url, output, branch, depth)
    if not repo:
        return

    log.log("Fetching changes...")
    repo.remote().fetch()
    log.log("Checking for local untracked files")
    rename_local_untracked(repo)
    log.log("Restoring locally deleted files")
    reset_deleted_files(repo)
    log.log("Unstaging all changes")
    repo.git.reset("--mixed")
    util.update_repo_config(repo)
    if repo.is_dirty():
        log.log("Repo is dirty. Commiting....")
        repo.git.commit("-am", "Automatic commit by urnc", "--allow-empty")
        log.log("Created new commit")

    log.log("Merging from remote...")
    merge(repo)
    log.log("Done.")


def clone(git_url, output, branch, depth):
    """
    Pull (or clone) a remote git repository, but only do a fast-forward pull.

    Args:
        git_url (str): The URL of the git repository to pull.
        output (str): The name of the output folder.
        branch (str): The branch to pull.
        depth (int): The depth for git fetch.

    Returns:
        None

    Raises:
        Does not raise any exceptions, but logs errors and warnings.
        This is required because this function may be called from a jupyter postStart hook,
        and exception would prevent the notebook from starting.
    """
    repo = get_repo(git_url, output, branch, depth)
    if not repo:
        return
    log.log("Pulling...")
    repo.git.pull("--ff-only")
    log.log("Done")
