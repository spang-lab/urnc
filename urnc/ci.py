import os
import shutil
import click
import git
import urnc.util as util
import urnc.logger as log

from urnc.convert import convert_fn


def clone_student_repo(config):
    repo_name = "student"
    # url = get_student_remote(config)
    url = util.get_config_value(
        config, "git", "student", required=True)
    base_path = os.path.dirname(os.getcwd())
    repo_path = os.path.join(base_path, repo_name)
    log.log(f"Cloning student repo {url} to {repo_path}")
    repo = git.Repo.clone_from(url, repo_path)
    util.update_repo_config(repo)
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
    exclude = util.get_config_value(config, "git", "exclude", default=[])
    with open(student_gitignore, "a") as gitignore:
        for value in exclude:
            gitignore.write(f"{value}\n")


def update_index(repo):
    cached_files_str = repo.git.ls_files("-ci", "--exclude-standard")
    if (cached_files_str != ''):
        cached_files = cached_files_str.split("\n")
        print(f"Removing excluded files {cached_files}")
        repo.index.remove(cached_files, working_tree=False)
        repo.index.write()


@ click.command(help="Run the urnc ci pipeline, this creates a git branch with the converted files")
@ click.pass_context
def ci(ctx):
    log.setup_logger(use_file=False)
    config = util.read_config(ctx)
    repo = util.get_git_repo(ctx)
    if (repo.is_dirty()):
        raise Exception(f"Repo is not clean. Commit your changes.")

    student_repo = clone_student_repo(config)
    clear_repo(student_repo)
    copy_files(repo, student_repo)

    log.log("Converting files")
    convert_fn(ctx,
               input=repo.working_dir,
               output=student_repo.working_dir,
               force=True,
               verbose=True,
               dry_run=False
               )
    log.log("Notebooks converted")

    log.log("Updating .gitignore from config")
    write_gitignore(repo, student_repo, config)

    # Remove exclude files from active index
    log.log("Dropping cached files...")
    update_index(student_repo)

    log.log("Adding files and commiting")
    student_repo.git.add(all=True)
    student_repo.index.commit("urnc convert")
    log.log("Pushing student repo")
    student_repo.git.push()
    log.log("Done.")
