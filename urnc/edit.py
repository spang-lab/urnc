import re
import click


import urnc.util as util

@click.command(help="Edit the course, switch to main branch")
@click.pass_context
def edit(ctx):
    repo = util.get_git_repo(ctx)
    remote = repo.remote("origin")

    main_branch = "main"
    if not util.branch_exists(repo, main_branch):
        repo.git.remote("set-branches","--add", "origin", "main")

    repo.git.fetch("--all")
    repo.git.switch(main_branch)

