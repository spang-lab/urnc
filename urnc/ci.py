import click
import urnc.util as util

from urnc.convert import convert_fn



@click.command(help="Run the urnc ci pipeline, this creates a git branch with the converted files")
@click.pass_context
def ci(ctx):
    config = util.read_config(ctx)
    repo = util.get_git_repo(ctx)
    if(repo.is_dirty()):
        raise Exception(f"Repo is not clean. Commit your changes.")

    util.update_repo_config(repo, config)

    branch = util.get_config_value(config, "student", "git", "branch", required=True)
    origin_branch = f"origin/{branch}"

    commit = repo.head.commit
    
    if not util.branch_exists(repo, branch):
        print(f"Creating orphan branch {branch}")
        repo.git.checkout("--orphan", branch)
        repo.git.commit("--allow-empty", "-m", "Create Orphan Branch")
        repo.git.push("origin", branch)
    else:
        repo.git.switch(branch)
        repo.git.reset("--hard", origin_branch)

    repo.git.checkout(commit, "*", force=True)

    convert_fn(ctx,
               input=repo.working_dir,
               output=repo.working_dir,
               force=True,
               verbose=True
    )
    util.write_gitignore(repo, config)
    
    # Remove exclude files from active index
    cached_files_str = repo.git.ls_files("-ci", "--exclude-standard")
    if(cached_files_str != ''):
        cached_files = cached_files_str.split("\n")
        print(f"Removing excluded files {cached_files}")
        repo.index.remove(cached_files, working_tree=False)
        repo.index.write()
    repo.git.add(all=True)
    repo.index.commit("urnc convert")
    repo.git.push("origin", branch)





