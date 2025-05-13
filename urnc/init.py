import os
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, Union

import click
import git
from copy import deepcopy
from nbconvert.exporters.notebook import NotebookExporter
from nbformat import NotebookNode
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from ruamel.yaml import YAML


from urnc.logger import log


example_config = {
    "name": "Example Course",
    "semester": "semester",
    "description": "Description for your course",
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

example_gitignore = textwrap.dedent(
    """
    out/
    .ipynb_checkpoints/
    .jupyter/
    .vscode/
    .DS_Store
    """
).strip()


example_notebook = new_notebook(cells=[
    new_markdown_cell(
        "# Example Notebook\n\n" +
        "urnc detects cells by checking for keywords in markdown headers"
    ),
    new_code_cell(
        "print('This is a normal code cell.')"
    ),
    new_markdown_cell(
        "## Assignment 1\n\n" +
        "Assignments are detected by urnc."
    ),
    new_markdown_cell(
        "Cells after an assignment headers are part of the assignment."
    ),
    new_markdown_cell(
        "## Solution\n\n" +
        "Solutions are removed by the urnc ci command."
    ),
    new_code_cell(
        "## Solution\n\n" +
        "print('Solutions can also be in code cells.')"
    ),
    new_markdown_cell(
        "## Other headers\n" +
        "end the previous assignment."
    ),
])


def name_to_dirname(name: str) -> str:
    return re.sub(r"\W+", "_", name.lower())


def write_config(path: Path,
                 config: Dict[str, Any] = example_config) -> None:
    config_path = path.joinpath("config.yaml")
    yaml = YAML(typ="rt")
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f)
    except Exception as e:
        raise click.FileError(str(config_path), str(e))


def write_gitignore(path: Path,
                    content: str = example_gitignore
                    ) -> None:

    file_path = path.joinpath(".gitignore")
    with open(file_path, "w") as f:
        f.write(content)


def write_example_notebook(path: Path,
                           notebook: NotebookNode = example_notebook) -> None:
    nb_path = path.joinpath("example.ipynb")
    exporter = NotebookExporter()
    content, _ = exporter.from_notebook_node(notebook, {})
    with open(nb_path, "w", newline="\n") as f:
        _ = f.write(content)


def init(name: str = "Example Course",
         path: Union[str, None, Path] = None,
         url: Union[str, None, Path] = None,
         student_url: Union[str, None, Path] = None) -> git.Repo:
    """
    Initializes a new course repository with the following structure:

    ```
    <path>
    ├── .git
    ├── .gitignore
    ├── config.yaml
    └── example.ipynb
    ```

    Args:
        name: The name of the course.
        path: The directory path where the course will be created. If not
            provided, the path is derived from the course name.
        url: The git URL for the upstream repository. If a local file path
            ending in `.git` is provided, a bare repository will be created at
            that location and configured as the origin remote.
        student_url: The git URL for the student repository.
            If a local file path ending in `.git` is provided, a bare
            repository will be created at that location and configured as the
            student remote url in config.yaml.

    Raises:
        click.UsageError: If the target directory already exists and is not empty.
        click.FileError: If there is an error writing the configuration file.

    Returns:
        git.Repo: The initialized git repository object.

    Example:
        >>> repo = init(name="My Example Course")
        >>> print(repo.working_dir)
        /path/to/my_example_course
    """
    if path is None:
        path = Path(name_to_dirname(name))
    if isinstance(path, str):
        path = Path(path)
    if os.path.exists(path) and any(os.scandir(path)):
        raise click.UsageError(f"Directory {path} exists already and is not empty.")
    config = deepcopy(example_config)
    if student_url is not None:
        student_url = str(student_url)
        if not ("@" in student_url or ":" in student_url):
            os.makedirs(student_url, exist_ok=True)
            git.Repo.init(student_url, bare=True, initial_branch="main")
        assert isinstance(config["git"], dict) # Required to please type checker
        config["git"]["student"] = student_url
    config["name"] = name
    path.mkdir(parents=True, exist_ok=True)
    repo = git.Repo.init(path, initial_branch="main")
    write_gitignore(path)
    write_config(path, config)
    write_example_notebook(path)
    repo.git.add(all=True)
    repo.index.commit("Initial commit")
    if url is not None:
        url = str(url)
        if not ("@" in url or ":" in url):
            os.makedirs(url, exist_ok=True)
            git.Repo.init(url, bare=True, initial_branch="main")
        repo.create_remote("origin", url)
    log(f"Course {name} initialized at {path}")
    return repo
