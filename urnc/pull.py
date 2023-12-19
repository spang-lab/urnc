"""Fetch and merge the student repo"""
import os
import git
import datetime

import urnc.util as util

import urnc.logger as log


def get_upstream_changes(repo):
    branch_name = repo.active_branch
    changes = repo.git.diff(
        f"..origin/{branch_name}", "--name-status").split('\n')
    return changes


def get_upstream_deleted(repo):
    changes = get_upstream_changes(repo)
    files = []
    for change in changes:
        parts = change.split('\t', 1)
        if (len(parts) != 2):
            continue
        [ctype, file] = change.split('\t', 1)
        if (ctype == "D"):
            files.append(file)
    return files


def get_upstream_added(repo):
    changes = get_upstream_changes(repo)
    files = []
    for change in changes:
        parts = change.split('\t', 1)
        if (len(parts) != 2):
            continue
        [ctype, file] = parts
        if (ctype == "A"):
            files.append(file)
    return files


def get_course_info(course_name, output):
    base_url = os.getenv("GIT_URL")
    if not base_url:
        log.error("Failed to pull. Missing env var GIT_URL")
        return (None, None)

    if not course_name:
        try:
            git_repo = git.Repo(os.getcwd(), search_parent_directories=True)
            git_url = git_repo.remote().url
            if not git_url.startswith(base_url):
                log.error(f"Failed to pull. Invalid git remote_url {git_url}")
                return (None, None)
            folder_name = git_repo.working_dir
            return (git_url, folder_name)
        except Exception:
            log.error("Failed to pull no course_name given and not in a git repo")
            return (None, None)
    folder_name = output
    if not output:
        folder_name = course_name

    git_url = f"{base_url}{course_name}.git"
    return (git_url, folder_name)


def get_repo(folder_name):
    base_url = os.getenv("GIT_URL")
    if not base_url:
        log.error("Missing env var GIT_URL")
        return None
    try:
        git_repo = git.Repo(folder_name)
        git_url = git_repo.remote().url
        if not git_url.startswith(base_url):
            log.error(
                f"Invalid git remote_url {git_url} needs to start with {base_url}")
            return None
        return git_repo
    except Exception:
        log.error(f"{folder_name} is not a git repo")
        return None


def reset_deleted_files(repo):
    branch = repo.active_branch
    deleted_files = repo.git.ls_files("--deleted").split('\n')
    deleted_upstream = get_upstream_deleted(repo)
    for filename in deleted_files:
        if (not filename):
            continue
        if (filename in deleted_upstream):
            repo.git.checkout("HEAD", '--', filename)
        else:
            log.dbg(f"Restoring deleted file {filename}")
            repo.git.checkout(f"origin/{branch}", "--", filename)


def rename_file_with_timestamp(path):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    (folder, filename) = os.path.split(path)
    (basename, ext) = os.path.splitext(filename)
    new_filename = f"{basename}_{timestamp}{ext}"
    new_path = os.path.join(folder, new_filename)
    log.warn(
        f"Renaming {path} to {new_path}, to avoid merge conflict with local untracked files.")
    os.rename(path, new_path)


def rename_local_untracked(repo):
    added_files = get_upstream_added(repo)
    for filename in added_files:
        if (not filename):
            continue
        path = os.path.join(repo.working_dir, filename)
        if (os.path.exists(path)):
            rename_file_with_timestamp(path)


def merge(repo):
    branch = repo.active_branch
    remote_branch = f"origin/{branch}"
    try:
        repo.git.merge("-Xours", remote_branch)
    except git.GitCommandError as err:
        if "CONFLICT (modify/delete)" in str(err):
            log.warn(
                "Found a CONFLICT (modify/delete). Keeping the local file by commiting.")
            repo.git.commit(
                "-am", "Resolve CONFLICT (modify/delete)", "--allow-empty")
            return
        raise


def pull_admin(course_name, output, branch, depth):
    isAdmin = os.getenv('IS_ADMIN') == "1"
    if (not isAdmin):
        return
    if (not course_name):
        return
    base_url = os.getenv("GIT_URL_ADMIN")
    if (not base_url):
        log.error("Missing env var GIT_URL_ADMIN")
        return
    git_url = f"{base_url}{course_name}.git"
    folder_name = output
    if not output:
        folder_name = f"{course_name}-admin"

    if (not os.path.exists(folder_name)):
        log.log(f"{folder_name} does not exists. Cloning repo {git_url}")
        try:
            git.Repo.clone_from(git_url, folder_name,
                                branch=branch, depth=depth)
            log.log("Cloned successfully.")
        except Exception as err:
            log.error("Failed to clone repo. Error:")
            log.error(err)
    else:
        log.log(f"{folder_name} exists.")
        try:
            repo = git.Repo(folder_name)
            log.log(f"Pulling...")
            repo.git.pull("--ff-only")
            log.log(f"Done")

        except Exception as err:
            log.error(f"{folder_name} is not a git repo")


def pull(course_name, output, branch, depth):
    pull_admin(course_name, output, branch, depth)

    (git_url, folder_name) = get_course_info(course_name, output)
    if (not git_url or not folder_name):
        return

    if (not os.path.exists(folder_name)):
        log.log(f"{folder_name} does not exists. Cloning repo {git_url}")
        try:
            git.Repo.clone_from(git_url, folder_name, branch=branch, depth=depth)
            log.log("Cloned successfully.")
        except Exception as err:
            log.error("Failed to clone repo. Error:")
            log.error(err)
        return
    log.log(f"{folder_name} exists. Updating the repo")
    repo = get_repo(folder_name)
    if (not repo):
        return

    log.log(f"Fetching changes...")
    repo.remote().fetch()
    log.log(f"Checking for local untracked files")
    rename_local_untracked(repo)
    log.log(f"Restoring locally deleted files")
    reset_deleted_files(repo)
    log.log(f"Unstaging all changes")
    repo.git.reset("--mixed")

    util.update_repo_config(repo)
    if repo.is_dirty():
        log.log("Repo is dirty. Commiting....")
        repo.git.commit("-am", "Automatic commit by urnc", "--allow-empty")
        log.log("Created new commit")

    log.log("Merging from remote...")
    merge(repo)
    log.log("Done.")
