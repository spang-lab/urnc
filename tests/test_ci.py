from pathlib import Path
import tempfile

import nbformat
import urnc
import urnc.preprocessor.util as util


def test_ci():
    
    tmp = Path(tempfile.mkdtemp())
    course_name = "Example Course"
    admin_path = tmp / "example-course-admin"
    admin_url = tmp / "example-course-admin.git"
    student_path = tmp / "example-course"
    student_url = tmp / "example-course.git"
    urnc.init.init(course_name, admin_path, admin_url, student_url)

    config = urnc.config.read(admin_path)
    config["convert"]["write_mode"] = "overwrite"
    config["ci"]["commit"] = True
    urnc.ci.ci(config)
    urnc.pull.pull(student_url, student_path, "main", 1)

    nb = nbformat.read(student_path / "example.ipynb", as_version=4)
    cells = nb["cells"]
    print(cells)
    assert util.has_tag(cells[2], "assignment")
    assert util.has_tag(cells[2], "assignment-start")
    assert util.has_tag(cells[3], "assignment")
    assert not (student_path / "config.yaml").exists()
