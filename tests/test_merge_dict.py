from urnc.config import merge_dict

def test_merge_dict():
    source = {
        "source_only_value": 1,
        "source_only_dict": {
            "source_only_value": 2
        },
        "shared_value": 3,
        "shared_dict": {
            "source_only_value": 4,
            "shared_value": 5,
        },
    }
    target = {
        "target_only_value": -1,
        "target_only_dict": {
            "target_only_value": -2
        },
        "shared_value": -3,
        "shared_dict": {
            "target_only_value": -4,
            "shared_value": -5,
        },
    }
    expected_result = {
        "source_only_value": 1,
        "source_only_dict": {
            "source_only_value": 2
        },
        "target_only_value": -1,
        "target_only_dict": {
            "target_only_value": -2
        },
        "shared_value": 3,
        "shared_dict": {
            "source_only_value": 4,
            "target_only_value": -4,
            "shared_value": 5,
        },
    }
    result = merge_dict(source, target)
    assert result == expected_result
    assert result is target # merge modifes target in place
