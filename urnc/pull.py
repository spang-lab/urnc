import click
import os


import urnc.util as util


base_url_admin = "https://git.uni-regensburg.de/fids/"
base_url = "https://git.spang-lab.de/"


@click.command(help="Pull the course repo")
@click.argument(
    "course_name",
    type=str,
    required=True
)
@click.argument(
    "folder_name",
    type=str,
    required=False,
    default=None
)
@click.option("-b", "--branch", help="The branch to pull", default="main")
@click.option("-d", "--depth", help="The depth for git fetch", default=1)
@click.pass_context
def pull(ctx, course_name, folder_name, branch, depth):
    admin_access = os.getenv('JUPYTERHUB_ADMIN_ACCESS')

    if not folder_name:
        folder_name = course_name

    git_url = os.path.join(base_url, course_name)
    if(admin_access == "1"):
        folder_name = f"{folder_name}-admin"
        git_url = os.path.join(base_url_admin, course_name)

    print(f"Pulling {git_url} to {folder_name}")








