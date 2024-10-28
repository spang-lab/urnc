import enum
import re

from enum import StrEnum

import nbformat


class Keywords(StrEnum):
    ASSIGNMENT_DEPRECATED = r"^#+\s+Exercise `?([\w-]+)`?"
    ASSIGNMENT_START = r"^#+\s+Assignment `?([\w-]+)`?"
    SOLUTION = r"^###+\s+Solution"
    SKELETON = r"^###+\s+Skeleton"
    SOLUTION_END = r"^###+\s*$"
    HEADER = r"^#"


class Tags(StrEnum):
    SOLUTION = "solution"
    ASSIGNMENT = "assignment"
    ASSIGNMENT_START = "assignment-start"
    NORMAL = "normal"


def cell_preview(cell):
    short = cell.source[0:100]
    text = re.sub(r"[\s\n]+", " ", short)
    return "'%s...'" % text[0:50]


def has_tag(cell, tag):
    ltag = tag.lower()
    if "metadata" not in cell:
        return False
    if "tags" not in cell.metadata:
        return False
    for tag in cell.metadata.tags:
        if tag.lower() == ltag:
            return True
    return False


def has_tags(cell, tags):
    for tag in tags:
        if not has_tag(cell, tag):
            return False
    return True


def set_tag(cell, tag):
    if has_tag(cell, tag):
        return
    if "tags" not in cell.metadata:
        cell.metadata.tags = []
    cell.metadata.tags.append(tag)


def remove_tag(cell, tag):
    if not has_tag(cell, tag):
        return
    cell.metadata.tags.remove(tag)


def to_snake_case(string):
    return string.replace(r"\s+", "_").lower()


def string_to_byte(input):
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "KiB": 1024,
        "MiB": 1024**2,
        "GiB": 1024**3,
        "TiB": 1024**4,
    }
    match = re.match(r"(\d+(\.\d+)?)\s*(\w+)", input)
    if match:
        value, _, unit = match.groups()
        value = float(value)

        # Check if the unit is valid for conversion
        if unit in units:
            return int(value * units[unit])
        else:
            raise ValueError("Invalid unit")

    else:
        raise ValueError("Invalid format")
