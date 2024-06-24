# Temporary file for pulling in more tree interface from Bonsai project
# TODO: consider renaming public package to bonsai

from .walker_tree import WalkerTree
from collections import defaultdict
from collections import namedtuple


class Node():
    # Point is used to represent the position for a given node
    Point = namedtuple("Point", "x y")

    def __init__(self, id, position, parent_id=None):
        self.id = id
        self.position = position
        self.parent_id = parent_id


class Bonsai(WalkerTree):

    # Take in arbitrary 'node' type based on 'bonsai.models.Metric' first
    def __init__(self, nodes, serial_nodes):
        self._aug_nodes = self._augment_nodes(nodes, serial_nodes)
        # Nodes are stored in a dict of Node ID to the list of child Nodes
        self._nodes = {}

    def list_nodes(self):
        # Create list of nodes from dict values of _nodes dict:
        node_list = []
        for sublist in self._nodes.values():
            node_list.extend(sublist)

        return node_list

    def add_node(self, node, parent_id):
        nodes = self._nodes
        nodes[parent_id].append(node)
        node_dict = self._augment_nodes(nodes)
        w_tree = self._construct_walker_tree(node_dict)
        w_tree.position_tree()

        # Get calculated position for each node and save it
        for node in self._nodes:
            point = w_tree.get_position(str(node.id))
            node.position = point

        # return???

    def delete_node(self, node):
        # TODO: Do not allow deleting root node???
        if not node.parent_id:
            return False # FIXME: raise exception instead?

        self._nodes.pop(node.id)
        node_dict = self._augment_nodes(self._nodes)
        w_tree = self._construct_walker_tree(node_dict)
        w_tree.position_tree()

        # Get calculated position for each node and save it
        for node in self._nodes:
            point = w_tree.get_position(str(node.id))
            node.position = point

        # return???

    # FIXME - Should be a normal method, not a static method?
    @staticmethod
    # FIXME: fix this interface
    def _augment_nodes(nodes, serial_nodes):
        # Augment the tree nodes with additional information e.g. isLeaf
        child_count = defaultdict(int)
        for node in nodes:
            print(node)
            if node.parent:
                child_count[str(node.parent.id)] += 1

        node_dict = serial_nodes # pre-serialized nodes
        for node_id in node_dict.keys():
            # Mark nodes with indication of whether it is a leaf node or not
            node_dict[node_id]["isLeaf"] = False if child_count.get(node_id) else True

        return node_dict

    # FIXME - Should be a normal method, not a static method?
    @staticmethod
    def _construct_walker_tree(node_dict) -> WalkerTree:
        # Configure node-positioning tree
        t = WalkerTree(
            sibling_separation=50, subtree_separation=100, level_separation=275, max_depth=100, node_size=250
        )
        # Construct parent to children dict
        parent_children_dict = {}
        root_node = None
        for node in node_dict.values():
            parent_id = str(node["parent"]) if node["parent"] else None
            if not parent_id:
                root_node = node
                continue
            if parent_id in parent_children_dict:
                parent_children_dict[parent_id].append(node)
            else:
                parent_children_dict[parent_id] = [node]

        # Sort children nodes by their x-coordinates
        for parent_id, children in parent_children_dict.items():
            parent_children_dict[parent_id] = sorted(children, key=lambda c: c["left"])

        # Add nodes augmented with relational data to the walker tree
        # Add root node as it is the only one who is not a child of anyone
        root_id = root_node["id"]
        root_first_child = None
        if root_id in parent_children_dict:
            root_children = parent_children_dict[root_id]
            if root_children:
                root_first_child = str(root_children[0]["id"])
        nodes = {
            t.Node(
                node_id=root_id,
                is_leaf=root_node["isLeaf"],
                left_sibling=None,
                right_sibling=None,
                parent=None,
                first_child=root_first_child,
            )
        }
        for parent_id, children in parent_children_dict.items():
            for i, child in enumerate(children):
                child_id = str(child["id"])
                left_sibling = None
                right_sibling = None
                first_child = None
                if i > 0:
                    left_sibling = children[i - 1]["id"]
                if i < len(children) - 1:
                    right_sibling = children[i + 1]["id"]
                if child_id in parent_children_dict:
                    child_children = parent_children_dict[child_id]
                    if child_children:
                        first_child = str(child_children[0]["id"])
                nodes.add(
                    t.Node(
                        node_id=child_id,
                        is_leaf=child["isLeaf"],
                        left_sibling=left_sibling,
                        right_sibling=right_sibling,
                        parent=parent_id,
                        first_child=first_child,
                    )
                )
        t.populate_tree(nodes)
        return t
