import click
import yaml
import tomllib
import tomli_w
import git
import os


def branch_exists(repo, branch):
    origin_branch = f"origin/{branch}"
    for ref in repo.references:
        if (ref.name == branch or ref.name == origin_branch):
            return True
    return False


def update_repo_config(repo):
    try:
        r = repo.config_reader()
        name = r.get_value("user", "name")
        email = r.get_value("user", "email")
        assert (name is not None)
        assert (email is not None)
        print(f"Repo user is {name}<{email}>")
        return
    except Exception:
        pass

    config_writer = repo.config_writer()
    config_writer.set_value("user", "name", "urnc")
    config_writer.set_value("user", "email", "urnc@spang-lab.de")
    config_writer.release()


def get_config_value(config, *args, default=None, required=False):
    value = config
    full_key = "config"
    for key in args:
        full_key = f"{full_key}.{key}"
        if key not in value:
            if required:
                raise Exception(f"{full_key} is required")
            return default
        value = value[key]
    return value


def get_git_repo(ctx):
    path = ctx.obj["ROOT"]
    try:
        git_repo = git.Repo(path, search_parent_directories=True)
        return git_repo
    except Exception:
        raise click.UsageError(
            f'The current working directory "{path}" is not a git repo'
        )


def get_git_root(ctx):
    repo = get_git_repo(ctx)
    return repo.working_dir


def read_config(ctx):
    filename = "config.yaml"
    base_path = get_git_root(ctx)

    path = os.path.join(base_path, filename)

    if not os.path.isfile(path):
        raise click.UsageError(
            f"urnc expects a config file called {filename} "
            f"in the git root folder '{base_path}' "
            "make sure you a in a course directory",
        )
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        raise click.FileError(path, str(e))


def write_config(ctx, data):
    filename = "config.yaml"
    base_path = get_git_root(ctx)

    path = os.path.join(base_path, filename)
    try:
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return path
    except Exception as e:
        raise click.FileError(path, str(e))


def read_pyproject(ctx):
    filename = "pyproject.toml"
    base_path = get_git_root(ctx)

    path = os.path.join(base_path, filename)

    try:
        with open(path, "rb") as f:
            config = tomllib.load(f)
            return config
    except Exception as e:
        raise click.FileError(path, str(e))


def write_pyproject(ctx, data):
    filename = "pyproject.toml"
    base_path = get_git_root(ctx)

    path = os.path.join(base_path, filename)
    try:
        with open(path, "wb") as f:
            tomli_w.dump(data, f)
            return path
    except Exception as e:
        raise click.FileError(path, str(e))
