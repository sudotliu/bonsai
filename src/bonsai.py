# FIXME: consider renaming public package to bonsai?

from .walker_tree import WalkerTree
from collections import defaultdict
from collections import namedtuple

from typing import DefaultDict, List



# Point is used to represent the position for a given node
Point = namedtuple("Point", "x y")

class InputNode:
    def __init__(self, id: str, parent_id: str, is_leaf: bool):
        self.id = id
        self.is_leaf = is_leaf

class BonsaiNode:
    def __init__(self, id: str, position, parent_id=None):
        self.id = id
        self.position = position
        self.parent_id = parent_id

# FIXME: should this inherit from WalkerTree?
class Bonsai:

    # The input is a dict of Parent Node ID to the list of child nodes,
    # where each child node is an instance of 'InputNode' and each list of
    # child nodes is sorted in the order that they should be positioned from
    # left to right.
    def __init__(self, tree: DefaultDict[str, List[InputNode]]):
        self._w_tree = self._construct_walker_tree(tree)

    def list_nodes(self):
        # Create list of nodes from dict values of _nodes dict:
        node_list = []
        for sublist in self._nodes.values():
            node_list.extend(sublist)

        return node_list

    def add_node(self, node, parent_id):
        self._nodes[parent_id].append(node)
        node_dict = self._augment_nodes()
        w_tree = self._construct_walker_tree(node_dict)
        w_tree.position_tree()

        # Get calculated position for each node and save it
        for node in self._nodes:
            point = w_tree.get_position(str(node.id))
            node.position = point

    def delete_node(self, node):
        # TODO: Do not allow deleting root node???
        if not node.parent_id:
            return False # FIXME: raise exception instead?

        self._nodes.pop(node.id)
        node_dict = self._augment_nodes()
        w_tree = self._construct_walker_tree(node_dict)
        w_tree.position_tree()

        # Get calculated position for each node and save it
        for node in self._nodes:
            point = w_tree.get_position(str(node.id))
            node.position = point

    # FIXME: fix this interface
    def _augment_nodes(self, serial_nodes=None):
        # Augment the tree nodes with additional information e.g. isLeaf
        child_count = defaultdict(int)
        for node in serial_nodes:
            if node.parent:
                child_count[str(node.parent.id)] += 1

        node_dict = serial_nodes # pre-serialized nodes
        if not node_dict:
            return None
        for node_id in node_dict.keys():
            # Mark nodes with indication of whether it is a leaf node or not
            node_dict[node_id]["isLeaf"] = False if child_count.get(node_id) else True

        return node_dict

    @staticmethod 
    def find_root(tree: DefaultDict[str, List[InputNode]]):
        # Collect all children in a set
        all_children_ids = set(child.id for children in tree.values() for child in children)

        # Identify nodes not in children set
        root_ids = [id for id in tree if id not in all_children_ids]

        # Error handling based on the number of potential roots
        if len(root_ids) == 1:
            return root_ids[0]
        elif len(root_ids) > 1:
            raise ValueError("Invalid tree input: multiple root nodes found")
        else:
            raise ValueError("Invalid tree input: no root node found")

    # FIXME - Should be a normal method, not a static method?
    def _construct_walker_tree(self, tree: DefaultDict[str, List[InputNode]]) -> WalkerTree:
        # Configure node-positioning tree
        # TODO: make these parameters configurable
        w_tree = WalkerTree(
            sibling_separation=50,
            subtree_separation=100,
            level_separation=275,
            max_depth=100,
            node_size=250,
        )
        if not tree:
            return w_tree

        # Find root node
        root_id = self.find_root_id(tree)
        # Find out if root node is a leaf which is only possible if the tree size is 1
        root_is_leaf = True if len(tree) == 1 else False

        # Add root node first as a special case since it has no parent
        root_children = tree[root_id]
        root_first_child = root_children[0].id if root_children else None
        nodes = {
            w_tree.WalkerNode(
                node_id=root_id,
                is_leaf=root_is_leaf,
                left_sibling=None,
                right_sibling=None,
                parent_id=None,
                first_child=root_first_child,
            )
        }
        # Build up Walker Tree using nodes augmented with "family" metadata
        for parent_id, children in tree.items():
            for i, child in enumerate(children):
                left_sibling = children[i - 1].id if i > 0 else None
                right_sibling = children[i + 1].id if i < len(children) - 1 else None
                first_child = tree[child.id][0].id if child.id in tree and tree[child.id] else None
                nodes.add(
                    w_tree.WalkerNode(
                        node_id=child.id,
                        is_leaf=child["isLeaf"],
                        left_sibling=left_sibling,
                        right_sibling=right_sibling,
                        parent_id=parent_id,
                        first_child=first_child,
                    )
                )

        w_tree.populate_tree(nodes)

        return w_tree
