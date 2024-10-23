import git


def git_folder_name(git_url):
    name = git_url.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def branch_exists(repo, branch):
    origin_branch = f"origin/{branch}"
    for ref in repo.references:
        if ref.name == branch or ref.name == origin_branch:
            return True
    return False


def get_repo(path):
    try:
        git_repo = git.Repo(path, search_parent_directories=True)
        return git_repo
    except Exception:
        return None


def set_commit_names(repo):
    try:
        r = repo.config_reader()
        name = r.get_value("user", "name")
        email = r.get_value("user", "email")
        assert name is not None
        assert email is not None
        return
    except Exception:
        pass

    config_writer = repo.config_writer()
    config_writer.set_value("user", "name", "urnc")
    config_writer.set_value("user", "email", "urnc@spang-lab.de")
    config_writer.release()
