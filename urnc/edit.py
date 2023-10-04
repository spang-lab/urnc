import re
import click


import urnc.util as util
import urnc.student as student

@click.command(help="Edit the course, switch to main branch")
@click.pass_context
def edit(ctx):
    repo = util.get_git_repo(ctx)

    main_branch = "main"
    if not util.branch_exists(repo, main_branch):
        repo.git.remote("set-branches","--add", "origin", "main")

    repo.git.fetch("--all")
    repo.git.switch(main_branch)
    idx = student.find_urnc_stash(repo)
    if(idx):
        repo.git.stash("pop", idx)

