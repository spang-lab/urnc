import os
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import click
import requests
from nbconvert.preprocessors.base import Preprocessor
from nbformat import NotebookNode
from traitlets.config import Bool, Unicode

import urnc.logger as log
import urnc.preprocessor.util as util


def url_is_valid(url: str) -> bool:
    try:
        response = requests.head(url, allow_redirects=True)
        is_valid = response.status_code == 200
        if not is_valid:
            log.warn(f"Request to {url} failed with code {response.status_code}")
        return is_valid
    except Exception:
        return False


class ImageChecker(Preprocessor):
    """
    A preprocessor that checks and validates image paths in Jupyter notebooks.

    This class ensures that images referenced in notebook cells are valid,
    checks their sizes, and optionally fixes invalid paths. It supports both
    local and remote images and provides interactive and automatic modes for
    fixing paths.
    """

    base_path = Unicode(".", help="The base path of the notebook").tag(config=True)
    max_image_size = Unicode("250 KiB", help="The maximum size of an image").tag(
        config=True
    )
    interactive = Bool(False, help="Interactive mode for fixing paths").tag(config=True)
    autofix = Bool(False, help="Automatically fix paths with a single valid fix").tag(
        config=True
    )
    invalid_tag = Unicode(
        None, help="Tag to assign to cells with invalid images", allow_none=True
    ).tag(config=True)

    def check_image(self, nb_path: Path, src: str) -> Tuple[bool, Optional[str]]:
        """
        Check the validity of an image path and optionally suggest fixes.

        This method validates whether an image exists, checks its size, and
        handles remote images. If the image is invalid, it attempts to find
        similar files and suggests fixes.

        Args:
            nb_path (Path): The path to the notebook file.
            src (str): The source path of the image.

        Returns:
            Tuple[bool, Optional[str]]: A tuple where the first element indicates
            whether the image is valid, and the second element is a suggested
            new path if applicable.
        """
        max_size = util.string_to_byte(self.max_image_size)
        if src.startswith("http"):
            log.warn(f"Remote image detected. {src}")
            if not url_is_valid(src):
                return False, None
            return True, None
        image_path = nb_path.parent.joinpath(src)
        if image_path.exists():
            try:
                stat = image_path.stat()
                image_size = stat.st_size
                if image_size > max_size:
                    rel_path = os.path.relpath(image_path, start=self.base_path)
                    log.warn(f"The image {rel_path} is larger than {self.max_image_size} KiB.")
                return True, None
            except Exception:
                log.warn(f"Could not retrieve the size of image {image_path}.")
                return False, None

        log.warn(f"The image {image_path} does not exists.")
        filename = image_path.name
        base_path = Path(self.base_path)
        matching_files = list(base_path.rglob(filename))
        if len(matching_files) == 1:
            file_path = matching_files[0]
            new_path = os.path.relpath(file_path, start=nb_path.parent).replace(os.sep, "/")
            log.warn(f"Found a similar file in the base path. Did you mean {file_path}?")
            if self.autofix:
                log.warn(f"Automatically fixing path to {matching_files[0]}")
                return False, str(new_path)
            if self.interactive and click.prompt(
                f'Do you want to change the path to "{new_path}"?', type=bool):
                return False, str(new_path)
            return False, None

        if len(matching_files) > 1:
            paths = [
                os.path.relpath(file_path, start=nb_path.parent)
                for file_path in matching_files
            ]
            log.log("Did you mean to write one of these?")
            log.log("[0]: continue")
            for i, path in enumerate(paths):
                log.log(f"{i + 1}: {path}")
            if not self.interactive:
                return False, None
            idx = click.prompt("Select the number of the path to use:", type=int)
            if idx > 0 and idx < len(paths):
                return False, paths[idx - 1]
            return False, None
        return False, None

    def replace_src(self, nb_path: Path, cell: NotebookNode, match: re.Match[str]):
        """
        Replace the source path of an image in a notebook cell.

        This method checks the validity of an image path and replaces it with a
        new path if a valid fix is found. It also assigns or removes tags for
        invalid images based on the `invalid_tag` attribute.

        Args:
            nb_path (Path): The path to the notebook file.
            cell: The notebook cell containing the image.
            match: A regex match object for the image source.

        Returns:
            str: The updated source path for the image.
        """
        text = match.group(0)
        src = match.group(1)
        is_valid, new_path = self.check_image(nb_path, src)
        if self.invalid_tag:
            if is_valid:
                util.remove_tag(cell, self.invalid_tag)
            else:
                util.set_tag(cell, self.invalid_tag)
        if new_path:
            log.warn(f"Changing path to {new_path}")
            log.warn(text.replace(src, str(new_path)))
            return text.replace(src, str(new_path))
        return text

    def preprocess(self, nb: NotebookNode, resources: Dict[str, Any]) -> Tuple[NotebookNode, Dict[str, Any]]:
        """
        Validate and fix image paths in a Jupyter notebook.

        Scans all cells in the notebook for image references, validates their
        paths, and replaces invalid paths with valid ones if possible. Both HTML
        and Markdown images are detected.

        Args:
            nb: The notebook object to preprocess.
            resources: Dictionary of resources associated with the notebook.
                Must contain at least the path to the notebook in the "path"
                key. Example: {"path": "/path/to/notebook"}

        Returns:
            Tuple: The updated notebook and resources.
        """
        nb_path = Path(resources["path"])
        img_regex = r'<img[^>]*src="([^"]*)"[^>]*>'
        md_img_regex = r"!\[[^\]]*\]\(([^)]*)\)"

        for cell in nb.cells:
            cell.source = re.sub(
                img_regex, lambda m: self.replace_src(nb_path, cell, m), cell.source
            )
            cell.source = re.sub(
                md_img_regex, lambda m: self.replace_src(nb_path, cell, m), cell.source
            )
        return nb, resources
