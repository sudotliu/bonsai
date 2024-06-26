from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, List, Tuple

from ._walker_tree import WalkerTree, WalkerNode, Point


@dataclass
class InputNode:
    id: str
    parent_id: str
    is_leaf: bool
    x: int


@dataclass
class Node:
    id: str
    pos: Point


class Bonsai:
    # The input is a dict of Parent Node ID to the list of child nodes,
    # where each child node is an instance of 'InputNode'.
    def __init__(self, tree: DefaultDict[str, List[InputNode]]):
        # _parent_id_to_children: main tree structure for tracking tree state
        self._parent_id_to_children = tree
        # _w_tree: instance of 'Walker Tree' built from our main tree
        self._w_tree = self._new_walker_tree()
        self._w_tree.position_tree()
        # _b_node_set: dictionary of ID to node for all nodes in tree, useful for quick lookups or
        # composing a flat list of nodes with position data.
        self._b_node_set: DefaultDict[str, Node] = defaultdict(None)
        for node_id in self._w_tree.get_all_node_ids():
            pos = self._w_tree.get_position(node_id)
            self._b_node_set[node_id] = Node(id=node_id, pos=pos)

    # Repositioning the 'Bonsai' tree covers all the high-level repeat work
    # needed each time the tree is updated, which includes:
    # - Reconstructing the underlying 'Walker Tree'
    # - Repositioning the 'Walker Tree' nodes
    # - Updating the positions of all Bonsai nodes
    def _reposition(self):
        self._w_tree = self._new_walker_tree()
        self._w_tree.position_tree()
        for b_node in self._b_node_set.values():
            self._b_node_set[b_node.id].pos = self._w_tree.get_position(b_node.id)

    def list_nodes(self) -> List[Node]:
        """
        Simple flat list of all tree nodes with minimal data required for positioning.
        """
        return list(self._b_node_set.values())

    def add_leaf(self, node: InputNode):
        """
        Adds a node to the tree as a new leaf node to the parent specified in the input. Once added,
        the tree is repositioned to ensure correct spacing. A small optimization could be to more
        minimally reposition the tree when the new node sits on the far left or right edges of the
        tree but does not seem worth the special-casing complexity at the moment.
        """
        if node in self._parent_id_to_children[node.parent_id]:
            raise ValueError("Node already exists in tree")

        #TODO: reconsider input type if only leaf nodes are allowed instead of
        # doing this check. Could potentially simplify input to just be flat
        # fields and default to MAX_BIG_INT for x value here or allow for specification
        # of adding a left or right leaf.
        if not node.is_leaf:
            raise ValueError("input must be a leaf i.e. have is_leaf=True")
        self._parent_id_to_children[node.parent_id].append(node)
        self._reposition()

    def prune(self, node_id: str, node_parent_id: str):
        """
        Removes a given tree node from the tree along with its entire subtree before repositioning
        the tree. This is a little less trivial than it sounds due to the care needed to ensure that
        all internal data structures are updated correctly prior to repositioning.
        """
        # Starting from the node to be deleted, queue up all children to be deleted
        # in a breadth-first manner. While queue is not empty, pop the first element
        # and add its children to queue before deleting that node from all structures.
        queue: List[Tuple[str, str]] = [(node_id, node_parent_id)]
        while queue:
            node_id, node_parent_id = queue.pop(0)
            if node_id in self._parent_id_to_children:
                for child in self._parent_id_to_children[node_id]:
                    queue.append((child.id, node_id))
            self._delete_node(node_id, node_parent_id)
            
        # Re-evaluate whether the deleted node's parent is now a leaf node
        if len(self._parent_id_to_children[node_parent_id]) == 0:
            # Traverse until you find the node_parent_id and update is_leaf
            for grandparent_id, nodes in self._parent_id_to_children.items():
                for i, node in enumerate(nodes):
                    if node.id == node_parent_id:
                        self._parent_id_to_children[grandparent_id][i].is_leaf = True
                        break
            # Remove parent key as it is no longer a parent but only if its not
            # the root node. TODO: perhaps this can be modeled better to avoid
            # root node special casing.
            if node_parent_id != self._w_tree.root_id():
                del self._parent_id_to_children[node_parent_id]
                
        # Reposition the tree after all subtree nodes have been deleted
        self._reposition()
        
    def _delete_node(self, node_id: str, node_parent_id: str):
        """
        Delete a single node from the tree along with its parent-child relationships.
        """
        # First remove node from any children lists in _input_tree
        for p_id, children in self._parent_id_to_children.items():
            if p_id != node_parent_id:
                continue
            self._parent_id_to_children[p_id] = [c for c in children if c.id != node_id]

        # Remove node as parent from keys of _input_tree
        if node_id in self._parent_id_to_children:
            del self._parent_id_to_children[node_id]

        # Remove node from _b_node_set
        if node_id in self._b_node_set:
            del self._b_node_set[node_id]

    def _root_is_leaf(self):
        if len(self._parent_id_to_children) == 0:
            raise ValueError("Invalid tree: no nodes found")
       
        return not self._parent_id_to_children[self._root_id()]

    def _root_id(self):
        # TODO: if we already have the root ID in Walker Tree, we could use that
        
        # Collect all children in a set
        child_ids = set(str(child.id) for children in self._parent_id_to_children.values() for child in children)

        # Identify potential root IDs i.e. those not in children set
        root_ids = [str(id) for id in self._parent_id_to_children if str(id) not in child_ids and id is not None]

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
    # NOTE: for improved performance, we might be able to avoid always
    # repositioning but it seems non-trivial
    def _new_walker_tree(self) -> WalkerTree:
        # Configure node-positioning tree
        # TODO: make these parameters configurable
        w_tree = WalkerTree(
            sibling_separation=50,
            subtree_separation=100,
            level_separation=275,
            max_depth=100,
            node_size=250,
        )
        if not self._parent_id_to_children:
            return w_tree

        # Sort children of each parent node by x-coordinate
        for parent_id, children in self._parent_id_to_children.items():
            self._parent_id_to_children[parent_id] = sorted(children, key=lambda c: c.x)

        # Add root node first as a special case since it has no parent
        root_id = self._root_id()
        root_children = self._parent_id_to_children[root_id]
        root_first_child = root_children[0].id if root_children else None
        nodes = {
            WalkerNode(
                node_id=root_id,
                is_leaf=self._root_is_leaf(),
                left_sibling=None,
                right_sibling=None,
                parent_id=None,
                first_child=root_first_child,
            )
        }
        # Build up Walker Tree using nodes augmented with "family" metadata
        for parent_id, children in self._parent_id_to_children.items():
            for i, child in enumerate(children):
                left_sibling = children[i - 1].id if i > 0 else None
                right_sibling = children[i + 1].id if i < len(children) - 1 else None
                child_has_children = child.id in self._parent_id_to_children and self._parent_id_to_children[child.id]
                first_child = self._parent_id_to_children[child.id][0].id if child_has_children else None
                nodes.add(
                    WalkerNode(
                        node_id=child.id,
                        is_leaf=child.is_leaf,
                        left_sibling=left_sibling,
                        right_sibling=right_sibling,
                        parent_id=parent_id,
                        first_child=first_child,
                    )
                )

        w_tree.populate_tree(nodes)

        return w_tree
