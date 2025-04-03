import re

from typing import List, Optional

from nbformat.notebooknode import NotebookNode


def starts_with(string: Optional[str], keywords: List[str]) -> bool:
    if string is None:
        return False
    for keyword in keywords:
        pattern = re.compile(rf"^\s*{keyword}\b", re.IGNORECASE)
        if re.match(pattern, string):
            return True
    return False


def cell_preview(cell: NotebookNode):
    short = cell.source[0:100]
    text = re.sub(r"[\s\n]+", " ", short)
    return "'%s...'" % text[0:50]


def has_tag(cell: NotebookNode, tag: str) -> bool:
    ltag = tag.lower()
    if "metadata" not in cell:
        return False
    if "tags" not in cell.metadata:
        return False
    for tag in cell.metadata.tags:
        if tag.lower() == ltag:
            return True
    return False


def has_tags(cell: NotebookNode, tags: List[str]) -> bool:
    for tag in tags:
        if not has_tag(cell, tag):
            return False
    return True


def set_tag(cell: NotebookNode, tag: str):
    if has_tag(cell, tag):
        return
    if "tags" not in cell.metadata:
        cell.metadata.tags = []
    cell.metadata.tags.append(tag)


def remove_tag(cell: NotebookNode, tag: str):
    if not has_tag(cell, tag):
        return
    cell.metadata.tags.remove(tag)


def to_snake_case(string: str) -> str:
    return string.replace(r"\s+", "_").lower()


def string_to_byte(input: str) -> int:
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
