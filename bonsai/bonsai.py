import logging
from dataclasses import dataclass
from typing import DefaultDict, List, Tuple

from ._walker_tree import WalkerTree, WalkerNode, Point
from .exceptions import *


log = logging.getLogger(__name__)


@dataclass
class Node:
    """
    Node is the basic unit of the tree and is used for both input and output.
    Take extra care to understand how the 'pos' (short for position) attribute
    works based on notes below as it may not be immediately obvious.
    
    Attributes:
        id (str): Unique identifier for the node.
        pos (Point): The position of the node in the tree.
            - Consider zero the center for x, so negative values go left, positive right.
            - NOTE: y is inverted, so zero is the top of the tree and positive values go down.
            - Also note that the y-coordinate in Point input is not important as it is recomputed.
        _is_leaf (bool): For internal use, no need to input, hence the underscore and default.
    """
    id: str
    pos: Point
    _is_leaf: bool = False

    
@dataclass(frozen=True)
class Config:
    """
    Configuration class for Bonsai tree positioning.
    The unit for all values should be roughly equatable to pixels when it comes
    to rendering the tree in a web application. The default values are based on
    the original application use-case and your mileage may vary.

    Attributes:
        sibling_separation (int): The separation between sibling nodes.
        subtree_separation (int): The separation between subtrees.
        level_separation (int): The separation between levels of the tree.
        max_depth (int): The maximum depth of the tree.
        node_size (int): The size (width) of each node in the tree.
    """
    sibling_separation: int = 50
    subtree_separation: int = 100
    level_separation: int = 275
    max_depth: int = 100
    node_size: int = 250


class Bonsai:
    # The input is a dict of Parent Node ID to the list of child nodes,
    # where each child node is an instance of 'InputNode'.
    def __init__(self, tree: DefaultDict[str, List[Node]], config: Config = Config()):
        # _parent_id_to_children: main tree structure for tracking tree state
        self._parent_id_to_children = tree
        self._validate()
        # Mark all leaf nodes in the tree
        self._mark_leaves()
        # _w_tree: instance of 'Walker Tree' built from our main tree
        self._w_tree_config = config
        self._w_tree_setup()
        self._w_tree.position_tree()
        
    def _validate(self):
        for p_id in self._parent_id_to_children.keys():
            if type(p_id) != str:
                raise ValueError("Node IDs must be strings")
        
    # Repositioning the 'Bonsai' tree covers all the high-level repeat work
    # needed each time the tree is updated, which includes:
    # - Reconstructing the underlying 'Walker Tree'
    # - Repositioning the 'Walker Tree' nodes
    # - Updating the positions of all Bonsai nodes
    def _reposition(self):
        self._mark_leaves()
        self._w_tree_setup()
        self._w_tree.position_tree()

    def list_nodes(self) -> List[Node]:
        """
        Return a simple list of all tree nodes with minimal data required for positioning.
        """
        nodes: List[Node] = []
        # Build up list of all Node types with positions from walker tree
        for parent_id, children in self._parent_id_to_children.items():
            pos = self._w_tree.get_position(parent_id)
            p_node = Node(id=parent_id, pos=pos, _is_leaf=False)
            nodes.append(p_node) if p_node not in nodes else None
            for child in children:
                pos = self._w_tree.get_position(child.id)
                c_node = Node(id=child.id, pos=pos, _is_leaf=child._is_leaf)
                nodes.append(c_node) if c_node not in nodes else None
            
        return nodes

    def add_leaf(self, node_id: str, parent_id: str):
        """
        Adds a node to the tree as a new leaf node to the parent specified in the input. Once added,
        the tree is repositioned to ensure correct spacing. A small optimization could be to more
        minimally reposition the tree when the new node sits on the far left or right edges of the
        tree but does not seem worth the special-casing complexity at the moment.
        Note: the new leaf is always added to the right of all existing siblings.
        """
        rightmost_sibling_x = 0
        for sibling in self._parent_id_to_children[parent_id]:
            rightmost_sibling_x = max(rightmost_sibling_x, sibling.pos.x)
            if sibling.id == node_id:
                raise ValueError("Node already exists in tree")
        
        # Update tree data structures
        self._parent_id_to_children[parent_id].append(
            Node(
                id=node_id,
                pos=Point(rightmost_sibling_x + 1, 0),
                _is_leaf=True,
            )
        )
        # Since we've added a leaf, we need to make sure to update the parent
        # node as no longer being a leaf node.
        self._update_is_leaf(parent_id, False)
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
            n_id, p_id = queue.pop(0)
            for child in self._parent_id_to_children[n_id]:
                queue.append((child.id, n_id))
            self._delete_node(n_id, p_id)
            
        # Re-evaluate whether the deleted node's parent is now a leaf node, which
        # is true if it has no children left.
        if len(self._parent_id_to_children[node_parent_id]) == 0:
            self._update_is_leaf(node_parent_id, True)
            # Remove parent key from our main structure as it is no longer a
            # parent if it has no children but ignore it if it's the root node.
            # The root node must stay in order to not pass an empty tree
            # structure downstream as that is invalid since there should be no
            # valid use-case for a tree with no nodes.
            if node_parent_id != self._w_tree.root_id():
                del self._parent_id_to_children[node_parent_id]
                
        # Reposition the tree after all subtree nodes have been deleted
        self._reposition()
        
    def _mark_leaves(self):
        for children in self._parent_id_to_children.values():
            for child in children:
                child._is_leaf = child.id not in self._parent_id_to_children
       
    def _update_is_leaf(self, node_id: str, is_leaf: bool):
        """
        Update the 'is_leaf' attribute of a node in the tree.
        """
        for parent_id, children in self._parent_id_to_children.items():
            for i, child in enumerate(children):
                if child.id == node_id:
                    self._parent_id_to_children[parent_id][i]._is_leaf = is_leaf
                    return
        
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

    def _root_is_leaf(self):
        if len(self._parent_id_to_children) == 0:
            raise ValueError("Invalid tree: no nodes found")
       
        return not self._parent_id_to_children[self._root_id()]

    def _root_id(self):
        try:
            if self._w_tree:
                return self._w_tree.root_id()
        except UnidentifiedRootNode:
            pass
        
        # Collect all children into a set
        child_ids = set(c.id for children in self._parent_id_to_children.values() for c in children)

        # Identify potential root IDs i.e. those not in children set
        root_ids = [id for id in self._parent_id_to_children if id not in child_ids]

        # Error handling based on the number of potential roots
        if len(root_ids) == 1:
            return root_ids[0]
        elif len(root_ids) > 1:
            log.error("Multiple root nodes found in tree: %s", root_ids)
            raise ValueError("Invalid tree input: multiple root nodes found")
        else:
            raise ValueError("Invalid tree input: no root node found")

    # This does most of the heavy lifting in terms of setting up the 'WalkerTree' which is used to
    # calculate new positions of the nodes in the tree. Note that the underlying 'WalkerTree' is
    # always created fresh here and saved into the instance variable '_w_tree'. For optimal
    # performance, we could potentially squash the layers to avoid always creating a brand new inner
    # tree, but that seems rather non-trivial and blends the concerns of the core algorithm with
    # the API and outer layer tree structure.
    def _w_tree_setup(self):
        # Configure node-positioning tree
        conf = self._w_tree_config
        self._w_tree = WalkerTree(
            sibling_separation=conf.sibling_separation,
            subtree_separation=conf.subtree_separation,
            level_separation=conf.level_separation,
            max_depth=conf.max_depth,
            node_size=conf.node_size,
        )
        if not self._parent_id_to_children:
            return

        # Sort children of each parent node by x-coordinate
        for parent_id, children in self._parent_id_to_children.items():
            self._parent_id_to_children[parent_id] = sorted(children, key=lambda c: c.pos.x)

        # Add root node first as a special case since it has no parent
        root_id = self._root_id()
        root_children = self._parent_id_to_children[root_id]
        root_first_child_id = root_children[0].id if root_children else None
        nodes = {
            WalkerNode(
                node_id=root_id,
                is_leaf=self._root_is_leaf(),
                left_sibling_id=None,
                right_sibling_id=None,
                parent_id=None,
                first_child_id=root_first_child_id,
            )
        }
        # Build up Walker Tree using nodes augmented with "family" metadata
        for parent_id, children in self._parent_id_to_children.items():
            for i, child in enumerate(children):
                left_sibling_id = children[i - 1].id if i > 0 else None
                right_sibling_id = children[i + 1].id if i < len(children) - 1 else None
                children_of_child = self._parent_id_to_children.get(child.id)
                first_child_id = children_of_child[0].id if children_of_child else None
                nodes.add(
                    WalkerNode(
                        node_id=child.id,
                        is_leaf=child._is_leaf,
                        left_sibling_id=left_sibling_id,
                        right_sibling_id=right_sibling_id,
                        parent_id=parent_id,
                        first_child_id=first_child_id,
                    )
                )

        self._w_tree.populate_tree(nodes)
