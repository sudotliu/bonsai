import pytest
from src.walker_tree import WalkerTree

def test_get_leftmost():
    pass
    # tree = WalkerTree(
    #     sibling_separation=10,
    #     subtree_separation=20,
    #     level_separation=30,
    #     max_depth=5,
    #     node_size=40,
    #     min_x=-100,
    #     max_x=100,
    #     min_y=-100,
    #     max_y=100,
    # )
    # # Create nodes for testing
    # node1 = WalkerTree.Node("1", False, None, None, None, "2")
    # node2 = WalkerTree.Node("2", False, None, None, None, "3")
    # node3 = WalkerTree.Node("3", True, None, None, None, None)
    # # Add nodes to the tree
    # tree._tree = {"1": tree._InternalNode(node1), "2": tree._InternalNode(node2), "3": tree._InternalNode(node3)}
    # # Test when level is greater than max_depth
    # assert tree._get_leftmost(tree._get_node("1"), 6, tree.max_depth) is None
    # # Test when node is a leaf
    # assert tree._get_leftmost(tree._get_node("3"), 0, tree.max_depth) is None
    # # Test when node has a leftmost descendant
    # assert tree._get_leftmost(tree._get_node("1"), 0, tree.max_depth) == tree._get_node("3")