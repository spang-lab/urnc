from nbconvert.preprocessors.base import Preprocessor

import os
import re
import urnc.preprocessor.util as util
import urnc.logger as log
from urnc.preprocessor.util import Keywords, Tags


def check_image(base_folder, src):
    if src.startswith("http"):
        log.warn("Remote image detected.")
        return
    image_path = os.path.normpath(os.path.join(base_folder, src))
    if (not os.path.exists(image_path)):
        log.warn(f"The image {image_path} does not exists.")


class BrokenLinks(Preprocessor):
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
