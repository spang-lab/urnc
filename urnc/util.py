import yaml
import git
import os


def get_git_repo():
    path = os.getcwd()
    try:
        git_repo = git.Repo(path, search_parent_directories=True)
    except Exception:
        print(f"Error: {path} is not in a git repo")
        return None
    return git_repo


def get_git_root():
    repo = get_git_repo()
    print(repo.working_dir)


def read_config():
    print("tmp")
