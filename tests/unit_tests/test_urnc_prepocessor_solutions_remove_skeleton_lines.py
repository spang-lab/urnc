from urnc.preprocessor.solutions import remove_skeleton_lines

def test_urnc_preprocessor_solutions_remove_skeleton_lines():
    assert all([
        remove_skeleton_lines("### Skeleton\n# # a == ?") == "",
        remove_skeleton_lines("### Skeleton\n# # a == ?\n###") == "###",
        remove_skeleton_lines("### Solution\na = 100\n### Skeleton\n# # a == ?\n###") == "### Solution\na = 100\n###"
    ])
