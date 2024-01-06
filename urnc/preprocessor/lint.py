from nbconvert.preprocessors.base import Preprocessor

import os
import re
import requests
import urnc.preprocessor.util as util
from urnc.preprocessor.util import Keywords, Tags
import urnc.logger as log


def url_is_valid(url):
    try:
        response = requests.head(url, allow_redirects=True)
        is_valid = response.status_code == 200
        if not is_valid:
            log.warn(f"Got response code {response.status_code}")
        return is_valid
    except Exception:
        return False


def check_image(base_folder, src):
    max_size_str = "250 KiB"
    max_size = util.string_to_byte(max_size_str)
    if src.startswith("http"):
        log.warn(f"Remote image detected. {src}")
        if not url_is_valid(src):
            log.warn(f"Request to {src} failed.")
        return
    image_path = os.path.normpath(os.path.join(base_folder, src))
    if os.path.exists(image_path):
        try:
            image_size = os.path.getsize(image_path)
            if image_size > max_size:
                log.warn(f"The image {image_path} is larger than {max_size_str} KiB. This will increase the loading time of your notebook. Consider compressing the image.")
        except Exception:
            log.warn(f"Could not retrieve the size of image {image_path}.")
    else:
        log.warn(f"The image {image_path} does not exists.")


class Linter(Preprocessor):
    def preprocess(self, notebook, resources):
        path = resources["path"]

        base_folder = os.path.dirname(path)

        for cell in notebook.cells:
            matches = re.findall(Keywords.IMAGE_TAG, cell.source)
            for match in matches:
                log.dbg(f"Detected html image tag with src {match}")
                check_image(base_folder, match)

            matches = re.findall(Keywords.MD_IMAGE_TAG, cell.source)
            for match in matches:
                (alt, src) = match
                log.dbg(f"Detected markdown image tag with src {src}")
                check_image(base_folder, src)

        return notebook, resources
