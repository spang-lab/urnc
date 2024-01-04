"""Toggle between main and student version of the course"""
import urnc


def edit():
    """Deprecated. Do not use anymore. Will be removed in 2.0.0."""
    repo = urnc.util.get_course_repo()
    main_branch = "main"
    if not urnc.util.branch_exists(repo, main_branch):
        repo.git.remote("set-branches","--add", "origin", "main")
    repo.git.fetch("--all")
    repo.git.switch(main_branch)
    idx = urnc.student.find_urnc_stash(repo)
    if(idx):
        repo.git.stash("pop", idx)

