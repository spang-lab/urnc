from traitlets.config import Config
from urnc.preprocessor.solutions import LineTags, SolutionProcessor

import nbformat
import textwrap


def test_tag_line():
    processor = SolutionProcessor()
    line = "## Solution"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.SOLUTION_KEY

    line = "## Skeleton"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.SKELETON_KEY

    line = "## End"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.END_KEY

    line = " ## End"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.END_KEY

    line = "   ###### End"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.END_KEY

    line = "###"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.END_KEY

    line = "## Random"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.NONE

    line = "Random"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.NONE

    line = "# Solution"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.NONE

    line = "# Skeleton"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.NONE

    line = "   # skeleton"
    tag, _ = processor.tag_line(line)
    assert tag == LineTags.NONE


def test_scan_lines():
    processor = SolutionProcessor()
    text = "## Solution\n solution\n## Skeleton\n# Code\n## End \nRandom"
    tags = [tag for tag, _ in processor.scan_lines(text)]
    assert tags == [
        LineTags.SOLUTION_KEY,
        LineTags.SOLUTION,
        LineTags.SKELETON_KEY,
        LineTags.SKELETON,
        LineTags.END_KEY,
        LineTags.NONE,
    ]
    text = "## Solution\n Content \n Content \n## Skeleton\nRandom"
    tags = [tag for tag, _ in processor.scan_lines(text)]
    print(tags)
    assert tags == [
        LineTags.SOLUTION_KEY,
        LineTags.SOLUTION,
        LineTags.SOLUTION,
        LineTags.SKELETON_KEY,
        LineTags.SKELETON,
    ]
    text = "Random"
    tagged_lines = processor.scan_lines(text)
    assert tagged_lines == [(LineTags.NONE, "Random")]


def test_strip_solution():
    processor = SolutionProcessor()
    code = textwrap.dedent(
        """
        line 1
        ## Solution
        solution
        ## Skeleton
        # skeleton
        ## End
        line 2
        """
    ).strip()
    cell = nbformat.v4.new_code_cell(code)
    stripped = processor.strip_cell(cell)
    desired = textwrap.dedent(
        """
        line 1
        skeleton
        line 2
        """
    ).strip()
    assert stripped and stripped.source == desired

    cell = nbformat.v4.new_markdown_cell("Random")
    stripped = processor.strip_cell(cell)
    assert stripped is None


def test_strip_skeleton():
    config = Config()
    config.SolutionProcessor.output = "solution"
    processor = SolutionProcessor(config=config)
    code = textwrap.dedent(
        """
        line 1
        ## Solution
        solution
        ## Skeleton
        skeleton
        ## End
        line 2
        """
    ).strip()
    for tag, line in processor.scan_lines(code):
        print(f"{tag}: {line}")
    tags = [tag for tag, _ in processor.scan_lines(code)]
    assert tags == [
        LineTags.NONE,
        LineTags.SOLUTION_KEY,
        LineTags.SOLUTION,
        LineTags.SKELETON_KEY,
        LineTags.SKELETON,
        LineTags.END_KEY,
        LineTags.NONE,
    ]
    cell = nbformat.v4.new_code_cell(code)
    stripped = processor.strip_cell(cell)

    desired = textwrap.dedent(
        """
        line 1
        solution
        line 2
        """
    ).strip()

    assert stripped and stripped.source == desired

    cell = nbformat.v4.new_markdown_cell("Random")
    stripped = processor.strip_cell(cell)
    assert stripped and stripped.source == "Random"


def test_multiple_solutions():
    processor = SolutionProcessor()
    code = textwrap.dedent(
        """
        line 1
        ## Solution
        solution
        ## Skeleton 
        # skeleton
        ## End
        line 2
        ## Solution
        solution2
        ## Skeleton
        # skeleton2
        ## End
        """
    ).strip()
    cell = nbformat.v4.new_code_cell(code)
    stripped = processor.strip_cell(cell)
    desired = textwrap.dedent(
        """
        line 1
        skeleton
        line 2
        skeleton2
        """
    ).strip()
    assert stripped and stripped.source == desired

    cell = nbformat.v4.new_markdown_cell("Random")
    stripped = processor.strip_cell(cell)
    assert stripped is None


def test_non_solution_comments():
    processor = SolutionProcessor()
    code = textwrap.dedent(
        """
        print("fib(5) = 5")
        ### some comment
        def fib(n):
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a+b
            return a
        ### some comment
        fib(5)
        """
    ).strip()
    cell = nbformat.v4.new_code_cell(code)
    stripped = processor.strip_cell(cell)
    assert not stripped
