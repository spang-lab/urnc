import pathlib
import subprocess
import sys


def test_urnc_init(tmp_path: pathlib.Path):
    print("tmp_path", tmp_path)
    args = [sys.executable, "-m", "urnc", "init", "My Course", "-p", "my_course", "-t", "full"]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0
    assert pathlib.Path("my_course/images").is_dir()
    assert pathlib.Path("my_course/lectures/week1").is_dir()
    assert pathlib.Path("my_course/lectures/week1/lecture1.ipynb").is_file()
    assert pathlib.Path("my_course/lectures/week1/lecture2.ipynb").is_file()
    assert pathlib.Path("my_course/assignments").is_dir()
    assert pathlib.Path("my_course/assignments/week1.ipynb").is_file()
    assert pathlib.Path("my_course/config.yaml").is_file()
    assert pathlib.Path("my_course/.git").is_dir()
    assert pathlib.Path("my_course/.gitignore").is_file()
