import pytest
from src.walker_tree import WalkerTree

def test_valid_configuration():
    tree = WalkerTree(
        sibling_separation=10,
        subtree_separation=20,
        level_separation=30,
        max_depth=5,
        node_size=40,
        min_x=-100,
        max_x=100,
        min_y=-100,
        max_y=100,
    )
    # No exception should be raised
    tree._validate_config()

def test_invalid_configuration():
    with pytest.raises(Exception):
        tree = WalkerTree(
            sibling_separation=-10,
            subtree_separation=20,
            level_separation=30,
            max_depth=5,
            node_size=40,
            min_x=-100,
            max_x=100,
            min_y=-100,
            max_y=100,
        )
        tree._validate_config()

    with pytest.raises(Exception):
        tree = WalkerTree(
            sibling_separation=10,
            subtree_separation=-20,
            level_separation=30,
            max_depth=5,
            node_size=40,
            min_x=-100,
            max_x=100,
            min_y=-100,
            max_y=100,
        )
        tree._validate_config()
