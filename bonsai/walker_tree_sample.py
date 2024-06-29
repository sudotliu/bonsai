import logging

from _walker_tree import WalkerTree, WalkerNode

logging.basicConfig(level=logging.DEBUG)


# Configure tree
t = WalkerTree(
    # Use sample tree and configuration values from paper for easier verification
    sibling_separation=4,
    subtree_separation=4,
    level_separation=1,
    max_depth=100,
    node_size=2,
)
nodes = {
    WalkerNode(node_id="A", is_leaf=True, left_sibling_id=None, right_sibling_id="D", parent_id="E", first_child_id=None),
    WalkerNode(node_id="B", is_leaf=True, left_sibling_id=None, right_sibling_id="C", parent_id="D", first_child_id=None),
    WalkerNode(node_id="C", is_leaf=True, left_sibling_id="B", right_sibling_id=None, parent_id="D", first_child_id=None),
    WalkerNode(node_id="D", is_leaf=False, left_sibling_id="A", right_sibling_id=None, parent_id="E", first_child_id="B"),
    WalkerNode(node_id="E", is_leaf=False, left_sibling_id=None, right_sibling_id="F", parent_id="O", first_child_id="A"),
    WalkerNode(node_id="F", is_leaf=True, left_sibling_id="E", right_sibling_id="N", parent_id="O", first_child_id=None),
    WalkerNode(node_id="G", is_leaf=True, left_sibling_id=None, right_sibling_id="M", parent_id="N", first_child_id=None),
    WalkerNode(node_id="H", is_leaf=True, left_sibling_id=None, right_sibling_id="I", parent_id="M", first_child_id=None),
    WalkerNode(node_id="I", is_leaf=True, left_sibling_id="H", right_sibling_id="J", parent_id="M", first_child_id=None),
    WalkerNode(node_id="J", is_leaf=True, left_sibling_id="I", right_sibling_id="K", parent_id="M", first_child_id=None),
    WalkerNode(node_id="K", is_leaf=True, left_sibling_id="J", right_sibling_id="L", parent_id="M", first_child_id=None),
    WalkerNode(node_id="L", is_leaf=True, left_sibling_id="K", right_sibling_id=None, parent_id="M", first_child_id=None),
    WalkerNode(node_id="M", is_leaf=False, left_sibling_id="G", right_sibling_id=None, parent_id="N", first_child_id="H"),
    WalkerNode(node_id="N", is_leaf=False, left_sibling_id="F", right_sibling_id=None, parent_id="O", first_child_id="G"),
    WalkerNode(node_id="O", is_leaf=False, left_sibling_id=None, right_sibling_id=None, parent_id=None, first_child_id="E"),
}
t.populate_tree(nodes)
t.position_tree()

node_ids = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
for node_id in node_ids:
    point = t.get_position(node_id)
    print("Node: {}, x: {}, y: {}".format(node_id, point.x, point.y))
