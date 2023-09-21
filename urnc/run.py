import click
import urnc.util as util

from urnc.convert import convert_fn


@click.command(help="Run the full urnc pipeline")
@click.pass_context


def run(ctx):
    config = util.read_config(ctx)
    repo = util.get_git_repo(ctx)
    if(repo.is_dirty()):
        raise Exception(f"Repo is not clean. Commit your changes.")

    util.update_repo_config(repo, config)

    branch = util.get_config_value(config, "student", "git", "branch", required=True)
    origin_branch = f"origin/{branch}"
    
    if not util.branch_exists(repo, branch):
        print(f"Creating orphan branch {branch}")
        repo.git.checkout("--orphan", branch)
        repo.git.commit("--allow-empty", "-m", "Create Orphan Branch")
        repo.git.push("origin", branch)
    else:
        repo.git.switch(branch)
        repo.git.reset("--hard", origin_branch)

    repo.git.checkout("main", "*", force=True)

    convert_fn(ctx,
               input=repo.working_dir,
               output=repo.working_dir,
               force=True,
               verbose=True
    )
    repo.index.add("*")
    repo.index.commit("Test")
    repo.git.switch("main")





