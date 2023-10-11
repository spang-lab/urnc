import os
import click
import urnc.util as util
import urnc.logger as log

from urnc.convert import convert_fn


def read_environment():
    ci_keys = ["CI_SERVER_PROTOCOL",
               "CI_SERVER_HOST"]
    env_dict = {}
    for key in ci_keys:
        value = os.getenv(key)
        if (not value):
            raise click.UsageError(
                f"Did not find env variable {key}. This commmand should only run in a gitlab ci")
        env_dict[key] = value
    token_key = "GROUP_ACCESS_TOKEN"
    token = os.getenv(token_key)
    env_dict[token_key] = token
    return env_dict


def get_student_remote(config):
    env = read_environment()
    target_path = util.get_config_value(
        config, "git", "target_path", required=True)

    protocol = env["CI_SERVER_PROTOCOL"]
    token = env["GROUP_ACCESS_TOKEN"]
    host = env["CI_SERVER_HOST"]
    git_url = f"{protocol}://{token}@{host}/{target_path}"
    return git_url


@ click.command(help="Run the urnc ci pipeline, this creates a git branch with the converted files")
@ click.pass_context
def ci(ctx):
    log.setup_logger(use_file=False)
    config = util.read_config(ctx)
    repo = util.get_git_repo(ctx)
    commit = repo.head.commit
    if (repo.is_dirty()):
        raise Exception(f"Repo is not clean. Commit your changes.")
    util.update_repo_config(repo)

    student_url = get_student_remote(config)
    log.log(f"Pushing to {student_url}")

    remote_name = "student"
    if remote_name in repo.remotes:
        existing_remote = repo.remotes[remote_name]
        existing_remote.set_url(student_url)
    else:
        repo.create_remote(remote_name, student_url)

    student = repo.remote("student")
    student.fetch()

    log.log("Converting files")
    convert_fn(ctx,
               input=repo.working_dir,
               output=repo.working_dir,
               force=True,
               verbose=True,
               dry_run=False
               )
    log.log("Notebooks converted")

    log.log("Updating .gitignore from config")
    util.write_gitignore(repo, config)
    # Remove exclude files from active index
    log.log("Dropping cached files...")
    cached_files_str = repo.git.ls_files("-ci", "--exclude-standard")
    if (cached_files_str != ''):
        cached_files = cached_files_str.split("\n")
        print(f"Removing excluded files {cached_files}")
        repo.index.remove(cached_files, working_tree=False)
        repo.index.write()
    log.log("Adding files and commiting")
    repo.git.add(all=True)
    repo.index.commit("urnc convert")
    log.log("Pushing to student remote")
    repo.git.push("-u", remote_name, "HEAD:refs/heads/main")
    repo.git.reset("--hard", commit)
