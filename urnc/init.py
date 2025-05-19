import os
import re
import textwrap
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Union

import click
import git
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from nbconvert.exporters.notebook import NotebookExporter
from nbformat import NotebookNode
from nbformat.v4 import new_code_cell as pyc
from nbformat.v4 import new_markdown_cell as mdc
from nbformat.v4 import new_notebook
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
    mdc("# Example Notebook\n\n" +
        "urnc detects cells by checking for keywords in markdown headers"),
    pyc("print('This is a normal code cell.')"),
    mdc("## Assignment 1\n\n" +
        "Assignments are detected by urnc."),
    mdc("Cells after an assignment headers are part of the assignment."),
    mdc("## Solution\n\n" +
        "Solutions are removed by the urnc ci command."),
    pyc("## Solution\n\n" +
        "print('Solutions can also be in code cells.')"),
    mdc("## Other headers\n" +
        "end the previous assignment."),
])

example_lecture_1 = new_notebook(cells=[
    mdc("# Lecture 1"),
    mdc("## Assignment 1\n" +
        "Print Hello World"),
    pyc("### Solution\n" +
        "print('Hello World')\n" +
        "### Skeleton\n" +
        "# Enter your solution here\n" +
        "###")
])

example_lecture_2 = new_notebook(cells=[
    mdc("# Lecture 2"),
    mdc("## Images"),
    mdc("### Blue Rectangle\n\n" +
        "The following image shows a blue rectangle.\n\n" +
        "![Blue Rectangle](../../images/blue_rectangle.svg)"),
    mdc("### Red Circle\n\n" +
        "The following image shows a red circle.\n\n" +
        "![Red Circle](../../images/red_circle.svg)\n"),
    mdc("### Assignment\n" +
        "Create a circle, rectangle or triangle with a color of your choice:\n"),
    pyc("### Solution\n" +
        "import matplotlib.pyplot as plt\n" +
        "from matplotlib.patches import Circle\n" +
        "fig, ax = plt.subplots()\n" +
        "circle = Circle((0.5, 0.5), 0.4, color='green')\n" +
        "ax.add_patch(circle)\n" +
        "ax.set_aspect('equal')\n" +
        "ax.axis('off')\n" +
        "plt.show()\n" +
        "### Skeleton\n" +
        "# Enter your solution here\n" +
        "###"
        )
])

example_assignments_1 = new_notebook(cells=[
    mdc("# Exercise Sheet Week 1"),
    mdc("## Assignment 1\n" +
        "Print your name"),
    pyc("### Solution\n" +
        "print('your name')\n" +
        "### Skeleton\n" +
        "# Enter your solution here\n" +
        "###"),
    mdc("## Assignment 2\n" +
        "Print the sum of the numbers from 1 to 100"),
    pyc("### Solution\n" +
        "print(sum(range(1, 101)))\n" +
        "### Skeleton\n" +
        "# Enter your solution here\n" +
        "###")
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


def write_notebook(path: Path, notebook: NotebookNode = example_notebook) -> None:
    exporter = NotebookExporter()
    content, _ = exporter.from_notebook_node(notebook, {})
    with open(path, "w", newline="\n") as f:
        _ = f.write(content)


def init(name: str = "Example Course",
         path: Union[str, None, Path] = None,
         url: Union[str, None, Path] = None,
         student_url: Union[str, None, Path] = None,
         template: str = "minimal") -> git.Repo:
    """
    Initializes a new course repository with the following structure:

        +-----------------------+------------------------------+
        | template=='minimal'   |   template=='full'           |
        +-----------------------+------------------------------+
        | <path>                |   <path>                     |
        | ├── .git              |   ├── .git                   |
        | ├── .gitignore        |   ├── .gitignore             |
        | ├── config.yaml       |   ├── config.yaml            |
        | └── example.ipynb     |   ├── images                 |
        |                       |   │   ├── blue_rectangle.svg |
        |                       |   │   └── red_circle.svg     |
        |                       |   ├── lectures               |
        |                       |   │   └── week1              |
        |                       |   │       ├── lecture1.ipynb |
        |                       |   │       └── lecture2.ipynb |
        |                       |   └── assignments            |
        |                       |       └── week1.ipynb        |
        +-----------------------+------------------------------+

    For details see https://spang-lab.github.io/urnc/usage.html

    Args:
        name: The name of the course.
        path: The directory path where the course will be created. If not
            provided, the path is derived from the course name.
        url: The git URL for the upstream repository. If a local file path
            is provided, a bare repository will be created at that location and
            configured as the origin remote.
        student_url: The git URL for the student repository.
            If a local file path is provided, a bare repository will be created
            at that location and configured as the student remote url in
            config.yaml.
        template: The template to use for the course. Can be "minimal" or "full".

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
        raise click.UsageError(
            f"Directory {path} exists already and is not empty.")
    config = deepcopy(example_config)
    if student_url is not None:
        student_url = str(student_url)
        if not _is_remote_git_url(student_url):
            os.makedirs(student_url, exist_ok=True)
            git.Repo.init(student_url, bare=True, initial_branch="main")
        # Required to please type checker
        assert isinstance(config["git"], dict)
        config["git"]["student"] = student_url
    config["name"] = name
    path.mkdir(parents=True, exist_ok=True)
    repo = git.Repo.init(path, initial_branch="main")
    write_gitignore(path)
    write_config(path, config)
    if template == "full":
        (path/"images").mkdir(exist_ok=True)
        (path/"lectures").mkdir(exist_ok=True)
        (path/"lectures/week1").mkdir(exist_ok=True)
        (path/"assignments").mkdir(exist_ok=True)
        write_notebook(path/"lectures/week1/lecture1.ipynb", example_lecture_1)
        write_notebook(path/"lectures/week1/lecture2.ipynb", example_lecture_2)
        write_notebook(path/"assignments/week1.ipynb", example_assignments_1)
        plot_shape("rectangle", "blue", path/"images/blue_rectangle.svg") # used by lecture 2
        plot_shape("circle", "red", path/"images/red_circle.svg") # used by lecture 2
    else:
        write_notebook(path/'example.ipynb', example_notebook)
    repo.git.add(all=True)
    repo.index.commit("Initial commit")
    if url is not None:
        url = str(url)
        if not _is_remote_git_url(url):
            os.makedirs(url, exist_ok=True)
            git.Repo.init(url, bare=True, initial_branch="main")
        repo.create_remote("origin", url)
    log(f"Course {name} initialized at {path}")
    repo.git.clear_cache()
    return repo


def _is_remote_git_url(url: str) -> bool:
    """Check if the given URL is pointing to a remote git repository."""
    url = url.strip()
    return (
        url.startswith(("http://", "https://", "git://", "ssh://")) or
        bool(re.match(r"^[\w\-]+@[\w\.\-]+:.*", url))
    )


def plot_shape(shape: str,
               color: str,
               path: Union[str, Path, None] = None,
               show: bool = False):
    """
    Draws a single shape (circle, rectangle, triangle) with the given color and saves as 64x64 SVG.

    Args:
        shape: Shape name ('circle', 'rectangle', 'triangle').
        color: Fill color as a string.
        path: File path to save the SVG image.
        show: If True, display the plot window.
    """
    fig, ax = plt.subplots(figsize=(2, 2), dpi=92)
    ax.set_aspect('equal')
    ax.axis('off')
    if shape.lower() == 'circle':
        patch = mpatches.Circle((0.5, 0.5), 0.4, color=color)
    elif shape.lower() == 'rectangle':
        patch = mpatches.Rectangle((0.1, 0.1), 0.8, 0.8, color=color)
    elif shape.lower() == 'triangle':
        patch = mpatches.Polygon(
            [[0.5, 0.9], [0.1, 0.1], [0.9, 0.1]], color=color)
    else:
        raise ValueError(f"Unknown shape: {shape}")
    ax.add_patch(patch)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    if path:
        plt.savefig(path, format='svg', bbox_inches='tight', pad_inches=0)
    if show:
        plt.show()
    plt.close(fig)
