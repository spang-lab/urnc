from typing import Optional, Tuple
import click
from nbconvert.preprocessors.base import Preprocessor

import re
import requests
from traitlets.config import Bool, Unicode
import urnc.preprocessor.util as util
import urnc.logger as log
from pathlib import Path


def url_is_valid(url):
    try:
        response = requests.head(url, allow_redirects=True)
        is_valid = response.status_code == 200
        if not is_valid:
            log.warn(f"Request to {url} failed with code {response.status_code}")
        return is_valid
    except Exception:
        return False


class ImageChecker(Preprocessor):
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
                    rel_path = image_path.relative_to(
                        Path(self.base_path), walk_up=True
                    )
                    log.warn(
                        f"The image {rel_path} is larger than {self.max_image_size} KiB."
                    )
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
            new_path = file_path.relative_to(nb_path.parent, walk_up=True)
            log.warn(
                f"Found a similar file in the base path. Did you mean {file_path}?"
            )
            if self.autofix:
                log.warn(f"Automatically fixing path to {matching_files[0]}")
                return False, str(new_path)
            if self.interactive and click.prompt(
                f'Do you want to change the path to "{new_path}"?', type=bool
            ):
                return False, str(new_path)
            return False, None

        if len(matching_files) > 1:
            paths = [
                file_path.relative_to(nb_path.parent, walk_up=True)
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

    def replace_src(self, nb_path: Path, cell, match):
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

    def preprocess(self, nb, resources):
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
