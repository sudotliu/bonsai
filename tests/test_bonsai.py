from collections import defaultdict

from src.bonsai import Bonsai, InputNode


def test_find_root():
    # Create a sample tree
    tree = defaultdict(list)
    tree["1"] = [InputNode("2", "1", False), InputNode("3", "1", False)]
    tree["2"] = [InputNode("4", "2", True)]
    tree["3"] = [InputNode("5", "3", True)]

    # Call the find_root method
    root = Bonsai.find_root(tree)

    # Assert that the root is correctly identified
    assert root == "1"