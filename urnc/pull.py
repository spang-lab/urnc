import click
import os
import git


import urnc.util as util

import urnc.logger as log

base_url_admin = "https://git.uni-regensburg.de/fids/"
base_url = "https://git.spang-lab.de/"


def get_upstream_changes(repo):
    branch_name = repo.active_branch
    changes = repo.git.diff(
        f"..origin/{branch_name}", "--name-status").split('\n')
    return changes


def get_upstream_deleted(repo):
    changes = get_upstream_changes(repo)
    files = []
    for change in changes:
        [ctype, file] = change.split('\t', 1)
        if (ctype == "D"):
            files.append(file)
    return files


def get_upstream_added(repo):
    changes = get_upstream_changes(repo)
    files = []
    for change in changes:
        [ctype, file] = change.split('\t', 1)
        if (ctype == "A"):
            files.append(file)
    return files


def get_remote_url(isAdmin, course_name, user, token):
    if not isAdmin:
        return f"https://git.spang-lab.de/{course_name}"
    return f"https://{user}:{token}@git.uni-regensburg.de/fids/{course_name}"


def get_folder_name(isAdmin, course_name, output):
    folder_name = output
    if output is None:
        folder_name = course_name
    if isAdmin:
        folder_name = f"{folder_name}-admin"
    return folder_name


def get_repo(folder_name):
    try:
        git_repo = git.Repo(folder_name)
        return git_repo
    except Exception:
        return log.critical(f"{folder_name} is not a git repo")


def reset_deleted_files(repo):
    branch = repo.active_branch
    deleted_files = repo.git.ls_files("--deleted").split('\n')
    deleted_upstream = get_upstream_deleted(repo)
    for filename in deleted_files:
        if (filename in deleted_upstream):
            repo.git.checkout("HEAD", '--', filename)
        else:
            log.dbg(f"Restoring deleted file {filename}")
            repo.git.checkout(f"origin/{branch}", "--", filename)


def merge(repo):
    branch = repo.active_branch


@ click.command(help="Pull the course repo")
@ click.argument(
    "course_name",
    type=str,
    required=True


)
@ click.option("-o", "--output", type=str, help="The name of the output folder", default=None)
@ click.option("-b", "--branch", help="The branch to pull", default="main")
@ click.option("-d", "--depth", help="The depth for git fetch", default=1)
@ click.option("-t", "--token", help="The git access token", required=True)
@ click.option("-u", "--user", help="The name of the access token", default="urnc")
@ click.pass_context
def pull(ctx, course_name, output, branch, depth, token, user):
    log.setup_logger()
    isAdmin = os.getenv('JUPYTERHUB_ADMIN_ACCESS') == "1"

    folder_name = get_folder_name(isAdmin, course_name, output)
    git_url = get_remote_url(isAdmin, course_name, user, token)

    if (not os.path.exists(folder_name)):
        log.log(f"{folder_name} does not exists. Cloning repo {git_url}")
        try:
            git.Repo.clone_from(git_url, folder_name,
                                branch=branch, depth=depth)
            log.log("Cloned successfully.")
        except Exception as err:
            log.error("Failed to clone repo. Error:")
            log.error(err)
        return
    log.log(f"{folder_name} exists. Updating the repo")
    repo = get_repo(folder_name)

    log.log(f"Fetching changes...")
    repo.remote().fetch()
    if (isAdmin):
        log.log(f"Trying to pull")
        repo.git.pull("--ff-only")
        log.log(f"Pulled repo. Done.")
        return

    log.log(f"Restoring locally deleted files")
    reset_deleted_files(repo)
    log.log(f"unstaging all changes")
    repo.git.reset("--mixed")

    if repo.is_dirty():
        log.log("Repo is dirty. Commiting....")
        repo.git.commit("-am", "Automatic commit by urnc",
                        "-c", "user.email=urnc@spang-lab.de",
                        "-c", "user.name=urnc",
                        "--allow-empty")
        log.log("Created new commit")

    log.log("Merging from remote...")
    merge(repo)
    log.log("Done.")
