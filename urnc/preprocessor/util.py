import enum
import re


class Keywords(str, enum.Enum):
    ASSIGNMENT_DEPRECATED = r"^### Exercise `?([\w-]+)`?"
    ASSIGNMENT_START = r"^### (?:Exercise|Assignment) `?([\w-]+)`?"
    SOLUTION = "### Solution"
    SKELETON = "### Skeleton"
    SOLUTION_END = "###"
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


def has_header(cell):
    if cell.cell_type != "markdown":
        return False
    if re.search(Keywords.SOLUTION, cell.source):
        return False
    if re.search("^#", cell.source):
        return True
    if re.search("\n#", cell.source):
        return True
    return False
