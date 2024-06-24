# FIXME: consider renaming public package to bonsai?
import json
from dataclasses import dataclass, asdict
from typing import DefaultDict, List, NamedTuple, Set

from .walker_tree import WalkerTree


# FIXME: redundant with walker Point?
# Point is used to represent the position for a given node
class Point(NamedTuple):
    x: int
    y: int

@dataclass(frozen=True)
class InputNode:
    id: str
    parent_id: str
    is_leaf: bool
    x: int

# TODO: reconsider this
def serialize_input_node(node):
    return json.dumps(asdict(node))

@dataclass
class BonsaiNode:
    id: str
    pos: Point

# FIXME: should this inherit from WalkerTree?
class Bonsai:

    # The input is a dict of Parent Node ID to the list of child nodes,
    # where each child node is an instance of 'InputNode' and each list of
    # child nodes is sorted in the order that they should be positioned from
    # left to right.
    # Note: values must be a List since order is important
    def __init__(self, tree: DefaultDict[str, List[InputNode]]):
        self._input_tree = tree
        self._w_tree = self._construct_walker_tree()
        self._w_tree.position_tree()
        self._b_node_set: DefaultDict[str, BonsaiNode] = {}
        id_set = self._w_tree.get_all_node_ids()
        for node_id in id_set:
            pos = self._w_tree.get_position(node_id)
            self._b_node_set[node_id] = BonsaiNode(id=node_id, pos=pos)

    # Repositioning the 'Bonsai' tree covers all the high-level repeat work
    # needed each time the tree is updated, which includes:
    # - Reconstructing the underlying 'Walker Tree'
    # - Repositioning the 'Walker Tree' nodes
    # - Updating the positions of all Bonsai nodes
    def _reposition(self):
        self._w_tree = self._construct_walker_tree()
        self._w_tree.position_tree()
        for b_node in self._b_node_set.values():
            self._b_node_set[b_node.id].pos = self._w_tree.get_position(b_node.id)

    def list_nodes(self) -> List[BonsaiNode]:
        return self._b_node_set.values()

    def add_node(self, node: InputNode):
        if node in self._input_tree[node.parent_id]:
            raise ValueError("Node already exists in tree")
        # Add new node to private _input_tree
        self._input_tree[node.parent_id].append(node)
        self._reposition()

    def delete_node(self, node_id: str):
        # First remove node from any children lists in _input_tree
        for children in self._input_tree.values():
            for i, child in enumerate(children):
                if child.id == node_id:
                    del children[i]
                    break

        # Remove node from keys of _input_tree
        if node_id in self._input_tree:
            del self._input_tree[node_id]

        self._reposition()

    def _root_is_leaf(self):
        return len(self._input_tree) == 1

    def _find_root_id(self):
        # Collect all children in a set
        child_ids = set(str(child.id) for children in self._input_tree.values() for child in children)

        # Identify potential root IDs i.e. those not in children set
        root_ids = [str(id) for id in self._input_tree if str(id) not in child_ids and id is not None]

        # Error handling based on the number of potential roots
        if len(root_ids) == 1:
            return root_ids[0]
        elif len(root_ids) > 1:
            raise ValueError("Invalid tree input: multiple root nodes found")
        else:
            raise ValueError("Invalid tree input: no root node found")

    # This does most of the heavy lifting in terms of constructing the 'WalkerTree'
    # which is used to calculate new positions of the nodes in the tree.
    # The tree is always repositioned in this call before being returned.
    # NOTE: for improved performance, we might be able to avoid always repositioning
    # but it seems non-trivial
    def _construct_walker_tree(self) -> WalkerTree:
        # Configure node-positioning tree
        # TODO: make these parameters configurable
        w_tree = WalkerTree(
            sibling_separation=50,
            subtree_separation=100,
            level_separation=275,
            max_depth=100,
            node_size=250,
        )
        if not self._input_tree:
            return w_tree

        # Sort children of each parent node by x-coordinate
        for parent_id, children in self._input_tree.items():
            self._input_tree[parent_id] = sorted(children, key=lambda c: c.x)

        # Add root node first as a special case since it has no parent
        root_id = self._find_root_id()
        root_children = self._input_tree[root_id]
        root_first_child = root_children[0].id if root_children else None
        nodes = {
            w_tree.WalkerNode(
                node_id=root_id,
                is_leaf=self._root_is_leaf(),
                left_sibling=None,
                right_sibling=None,
                parent_id=None,
                first_child=root_first_child,
            )
        }
        # Build up Walker Tree using nodes augmented with "family" metadata
        for parent_id, children in self._input_tree.items():
            for i, child in enumerate(children):
                left_sibling = children[i - 1].id if i > 0 else None
                right_sibling = children[i + 1].id if i < len(children) - 1 else None
                child_has_children = child.id in self._input_tree and self._input_tree[child.id]
                first_child = self._input_tree[child.id][0].id if child_has_children else None
                nodes.add(
                    w_tree.WalkerNode(
                        node_id=child.id,
                        is_leaf=child.is_leaf,
                        left_sibling=left_sibling,
                        right_sibling=right_sibling,
                        parent_id=parent_id,
                        first_child=first_child,
                    )
                )

        # TODO: is this hand-off necessary or can we cut redundancy here?
        w_tree.populate_tree(nodes)

        return w_tree
