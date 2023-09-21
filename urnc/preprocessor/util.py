import enum
import re


class Keywords(str, enum.Enum):
    EXERCISE_START = r"^### Exercise `?([\w-]+)`?"
    SOLUTION = "### Solution"
    SKELETON = "### Skeleton"
    SOLUTION_END = "###"


class Tags(str, enum.Enum):
    SOLUTION = "solution"
    EXERCISE = "exercise"
    EXERCISE_START = "exercise-start"
    SKELETON = "skeleton"


def cell_preview(cell):
    short = cell.source[0:100]
    text = re.sub(r"[\s\n]+", " ", short)
    return "'%s...'" % text[0:50]


def has_tag(cell, tag):
    ltag = tag.lower()
    if "tags" not in cell.metadata:
        return False
    for tag in cell.metadata.tags:
        if tag.lower() == ltag:
            return True
    return False


def set_tag(cell, tag):
    if has_tag(cell, tag):
        return
    if "tags" not in cell.metadata:
        cell.metadata.tags = []
    cell.metadata.tags.append(tag)


def has_header(cell):
    if cell.cell_type != "markdown":
        return False
    if re.search("^#", cell.source):
        return True
    if re.search("\n#", cell.source):
        return True
    return False
