import logging

import walker_tree as tree

logging.basicConfig(level=logging.DEBUG)


# Configure tree
t = tree.WalkerTree(sibling_separation=50, subtree_separation=100, level_separation=50, max_depth=100, node_size=300)
t.add_node(node_id="A", is_leaf=True, left_sibling=None, right_sibling="D", parent="E", first_child=None)
t.add_node(node_id="B", is_leaf=True, left_sibling=None, right_sibling="C", parent="D", first_child=None)
t.add_node(node_id="C", is_leaf=True, left_sibling="B", right_sibling=None, parent="D", first_child=None)
t.add_node(node_id="D", is_leaf=False, left_sibling="A", right_sibling=None, parent="E", first_child="B")
t.add_node(node_id="E", is_leaf=False, left_sibling=None, right_sibling="F", parent="O", first_child="A")
t.add_node(node_id="F", is_leaf=True, left_sibling="E", right_sibling="N", parent="O", first_child=None)
t.add_node(node_id="G", is_leaf=True, left_sibling=None, right_sibling="M", parent="N", first_child=None)
t.add_node(node_id="H", is_leaf=True, left_sibling=None, right_sibling="I", parent="M", first_child=None)
t.add_node(node_id="I", is_leaf=True, left_sibling="H", right_sibling="J", parent="M", first_child=None)
t.add_node(node_id="J", is_leaf=True, left_sibling="I", right_sibling="K", parent="M", first_child=None)
t.add_node(node_id="K", is_leaf=True, left_sibling="J", right_sibling="L", parent="M", first_child=None)
t.add_node(node_id="L", is_leaf=True, left_sibling="K", right_sibling=None, parent="M", first_child=None)
t.add_node(node_id="M", is_leaf=False, left_sibling="G", right_sibling=None, parent="N", first_child="H")
t.add_node(node_id="N", is_leaf=False, left_sibling="F", right_sibling=None, parent="O", first_child="G")
t.add_node(node_id="O", is_leaf=False, left_sibling=None, right_sibling=None, parent=None, first_child="E")

t.position_tree()

node_ids = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
for node_id in node_ids:
    point = t.get_position(node_id)
    print("Node: {}, x: {}, y: {}".format(node_id, point.x, point.y))
