import yaml
import git
import os


def get_git_root():
    path = os.getcwd()
    git_repo = git.Repo(path, search_parent_directories=True)

    print(git_repo)


def read_config():
    print("tmp")
