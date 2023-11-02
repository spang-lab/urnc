import enum
import re


class Keywords(str, enum.Enum):
    ASSIGNMENT_DEPRECATED = r"^#+ Exercise `?([\w-]+)`?"
    ASSIGNMENT_START = r"^#+ Assignment `?([\w-]+)`?"
    SOLUTION = "^#+ Solution"
    SKELETON = "^#+ Skeleton"
    SOLUTION_END = r"^#+\s*$"
    HEADER = r'^#'
    IMAGE_TAG = r'<img[^>]*src="([^"]*)"'
    MD_IMAGE_TAG = r"!\[([^\]]*)\]\(([^)]*)\)"
    ASSIGNMENT_LINK = r"\(#Assignment-.*\)"
    ASSIGNMENT_REPLACE = r"#Assignment-"


class Tags(str, enum.Enum):
    SOLUTION = "solution"
    ASSIGNMENT = "assignment"
    ASSIGNMENT_START = "assignment-start"
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


def to_snake_case(string):
    return string.replace(r'\s+', '_').lower()
