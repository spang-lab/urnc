import os, tempfile
import urnc
from pathlib import Path

os.chdir(tempfile.mkdtemp())

urnc.init.init()
urnc.convert.convert(
    config = urnc.config.default_config("example_course"),
    input = Path('example_course/example.ipynb').absolute(),
    targets = [{
        "type": "student",
        "path": "{nb.abspath}",
    }]
)
