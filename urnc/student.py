import click
import re


import urnc.util as util
from urnc.convert import convert_fn


def find_urnc_stash(repo):
    stash = repo.git.stash("list").split("\n")
    pattern = r'stash@{(?P<idx>\d+)}:[^:]+:\s+urnc'
    for line in stash:
        match = re.match(pattern, line)
        if match:
            return match.group("idx")
    return None




@click.command(help="Build and show the student version")
@click.pass_context
def student(ctx):
    repo = util.get_git_repo(ctx)
    if repo.active_branch.name != "main":
        raise Exception("You are not in the main branch")
    existing = find_urnc_stash(repo)
    if(existing):
        raise Exception("There are already stashed changes for urnc")

    repo.git.stash("push", "-m", "urnc")
    idx = find_urnc_stash(repo)
    if(not idx):
        raise Exception("Failed to stash changes properly")
    repo.git.checkout("-B", "urnc_tmp")
    repo.git.stash("apply", idx)
    convert_fn(ctx,
               input=repo.working_dir,
               output=repo.working_dir,
               force=True,
               verbose=True,
               dry_run=False
    )
    repo.git.add(all=True)
    repo.index.commit("urnc test convert")

