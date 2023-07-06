import click
import yaml
import git
import os


def get_git_repo():
    path = os.getcwd()
    try:
        git_repo = git.Repo(path, search_parent_directories=True)
        return git_repo
    except Exception:
        raise click.UsageError(
            f'The current working directory "{path}" is not a git repo'
        )


def get_git_root():
    repo = get_git_repo()
    return repo.working_dir


def read_config():
    config_filename = "config.yaml"
    base_path = get_git_root()
    path = os.path.join(base_path, config_filename)
    print(path)
