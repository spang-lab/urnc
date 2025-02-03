import re
import click
from nbconvert.exporters.notebook import NotebookExporter
import urnc
import textwrap
import nbformat
import git
from pathlib import Path
from ruamel.yaml import YAML

from urnc.logger import log


def name_to_dirname(name: str) -> str:
    return re.sub(r"\W+", "_", name.lower())


def write_config(path: Path, name: str):
    config_path = path.joinpath("config.yaml")
    config = {
        "name": name,
        "semester": "semester",
        "description": "description for your course",
        "version": "0.1.0",
        "authors": [
            {
                "name": "Your Name",
                "email": "YourEmail@host.com",
            }
        ],
        "git": {
            "student": "Link to student repo",
            "output_dir": "out",
            "exclude": [
                "config.yaml",
                "container/",
            ],
        },
    }
    yaml = YAML(typ="rt")
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f)
    except Exception as e:
        raise click.FileError(str(config_path), str(e))


def write_gitignore(path: Path):
    file_path = path.joinpath(".gitignore")
    file_content = textwrap.dedent(
        """
            out/
            .ipynb_checkpoints/
            .jupyter/
            .vscode/
            .DS_Store
            """
    ).strip()
    with open(file_path, "w") as f:
        f.write(file_content)


def write_notebook(path: Path, config: dict):
    cells = [
        nbformat.v4.new_markdown_cell(
            "# Example Notebook \n urnc detects cells by checking for keywords in markdown headers"
        ),
        nbformat.v4.new_code_cell("print('This is a normal code cell.')"),
        nbformat.v4.new_markdown_cell(
            "### Assignment 1 \n Assignments are detected by urnc."
        ),
        nbformat.v4.new_markdown_cell(
            "Cells after an assignment header are considered part of the assignment."
        ),
        nbformat.v4.new_markdown_cell(
            "### Solution \n Solutions are removed by the urnc ci command."
        ),
        nbformat.v4.new_code_cell(
            "### Solution \n print('Solutions can also be in code cells.')"
        ),
        nbformat.v4.new_markdown_cell(
            "## Other headers \n end the previous assignment."
        ),
    ]
    nb = nbformat.v4.new_notebook(cells=cells)
    nb_path = path.joinpath("example.ipynb")
    exporter = NotebookExporter()
    notebook, _ = exporter.from_notebook_node(nb, {})
    urnc.convert.write_notebook(notebook, nb_path, config)


def init(config, name):
    dirname = name_to_dirname(name)
    path = Path(config["base_path"]).joinpath(dirname)
    if path.exists() and any(path.iterdir()):
        raise click.UsageError(f"Directory {path} already exists as is not empty.")
    path.mkdir(parents=True, exist_ok=True)
    repo = git.Repo.init(path, initial_branch="main")
    write_gitignore(path)
    write_config(path, name)
    write_notebook(path, config)
    repo.git.add(all=True)
    repo.index.commit("Initial commit")
    log(f"Course {name} initialized at {path}")
    return repo
