"""
Python implementation based on John Q. Walker II's node-positioning
algorithm for general trees with some adjustments and additional methods.

http://www.cs.unc.edu/techreports/89-034.pdf

NB: there are select comments marked with NB (nota bene), which call to attention
parts of the algorithm that differ from the original specification because the original
specification appears to be wrong in those places. The changes made in these parts
were absolutely necessary for the algorithm to work as intended, so it is assumed that
these were typos in the original paper.
"""
from collections import namedtuple
import math
import logging
from typing import Optional, Set

from walker_tree import exceptions

log = logging.getLogger(__name__)

# Point is used to represent the position for a given node
Point = namedtuple("Point", "x y")


class WalkerTree:
    def __init__(
        self,
        sibling_separation: int,
        subtree_separation: int,
        level_separation: int,
        max_depth: int,
        node_size: int,
        # Optional configuration - see details in comments below
        min_x: int = -math.inf,
        max_x: int = math.inf,
        min_y: int = -math.inf,
        max_y: int = math.inf,
    ):
        # The algorithm maintains a list of the previous node at each level i.e. the adjacent neighbor to the left.
        # level_zero_ptr is a pointer to the first entry in this list.
        self._level_zero_ptr = None
        # Fixed distances used in the final walk of the tree to determine the absolute coordinates
        # of a node with respect to the apex node of the tree.
        self._x_top_adj = 0
        self._y_top_adj = 0

        # Required Settings
        # The minimum distance between adjacent siblings of the tree
        self.sibling_separation: int = sibling_separation
        # The minimum distance between adjacent subtrees of a tree.
        # For proper aesthetics, this value is normally somewhat larger than self.sibling_separation.
        self.subtree_separation: int = subtree_separation
        # The fixed distance between adjacent levels of the tree.
        # Used in determining the y-coordinate of a node being positioned.
        self.level_separation: int = level_separation
        # The maximum number of levels in the tree to be positioned.
        # If all levels are to be positioned, set this value to positive infinity (or an appropriate numerical value).
        self.max_depth: int = max_depth
        # The width of a node to be accounted for when calculating positioning.
        # For nodes of different sizes refer to original algorithm and use the MEAN_self.node_size calculations.
        self.node_size: int = node_size

        # Optional Settings
        # If set, these define the boundaries within which to position the tree nodes and nodes beyond
        # those extents will not be positioned. Otherwise, it is assumed that the coordinate plane is boundless.
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

        self._validate_configuration()

        # Tree is represented internally as a map of Node ID to the Node object
        self._tree = {}
        self._root_node_id = None

    def _validate_configuration(self):
        invalid_values = {}
        if self.sibling_separation < 0:
            invalid_values["sibling_separation"] = self.sibling_separation
        if self.subtree_separation < 0:
            invalid_values["subtree_separation"] = self.subtree_separation
        if self.level_separation < 0:
            invalid_values["level_separation"] = self.level_separation
        if self.max_depth < 0:
            invalid_values["max_depth"] = self.max_depth
        if self.node_size < 0:
            invalid_values["node_size"] = self.node_size
        if self.min_x >= self.max_x:
            invalid_values["min_x, max_x"] = (self.min_x, self.max_x)
        if self.min_y >= self.max_y:
            invalid_values["min_y, max_y"] = (self.min_y, self.max_y)
        if invalid_values:
            raise exceptions.InvalidTreeConfiguration("invalid values: {}".format(invalid_values))

    class Node:
        """Client-facing representation of a tree node used when populating the tree.

        Args:
            node_id: unique string identifier of the node
            is_leaf: boolean indicating whether this node is a leaf node i.e. does not have children
            left_sibling: ID of the node (with same parent) immediately to the left of this node, if any
            right_sibling: ID of the node (with same parent) immediately to the right of this node, if any
            parent: ID of the parent node, if any
            first_child: ID of the leftmost child of this node, if any
        """

        def __init__(
            self,
            node_id: str,
            is_leaf: bool,
            left_sibling: Optional[str],
            right_sibling: Optional[str],
            parent: Optional[str],
            first_child: Optional[str],
        ):
            self.id = node_id
            self.is_leaf = is_leaf
            self.left_sibling = left_sibling
            self.right_sibling = right_sibling
            self.parent = parent
            self.first_child = first_child

    class _InternalNode(Node):
        def __init__(self, node):
            super().__init__(
                node.id, node.is_leaf, node.left_sibling, node.right_sibling, node.parent, node.first_child
            )

            # The current node's preliminary x-coordinate
            self.prelim = 0
            # The current node's modifier value
            self.modifier = 0
            # The current node's nearest neighbor to the left, at the same level
            self.left_neighbor = None

            # Position coordinates of the node
            self.point = Point(0, 0)

        def has_child(self):
            return not self.is_leaf

        def has_left_sibling(self):
            return self.left_sibling is not None

        def has_right_sibling(self):
            return self.right_sibling is not None

        def __str__(self):
            left_neighbor_id = self.left_neighbor and self.left_neighbor.id
            return "id: {}, left_neighbor: {}, point: {}, prelim: {}, modifier: {}".format(
                self.id, left_neighbor_id, self.point, self.prelim, self.modifier,
            )

    def _get_leftmost(self, node, level, depth) -> Optional[_InternalNode]:
        """This function returns the leftmost descendant of a node at a given depth.
        This uses a postorder walk of the subtree under node, down to the level of depth.
        'level' here is not the absolute tree level but the level below the node whose
        leftmost descendant is being found.
        """
        if level >= depth:
            return node
        elif node.is_leaf:
            return None
        else:
            right_most = self._get_node(node.first_child)
            left_most = self._get_leftmost(right_most, level + 1, depth)
            # Do a postorder walk of the subtree below node
            while not left_most and right_most.has_right_sibling():
                right_most = self._get_node(right_most.right_sibling)
                left_most = self._get_leftmost(right_most, level + 1, depth)
            return left_most

    def _apportion(self, node, level):
        """Cleans up the positioning of small sibling subtrees.
        When moving a new subtree farther and farther to the right,
        gaps may open up among smaller subtrees that were previously
        sandwiched between larger subtrees. Thus, when moving the new,
        larger subtree to the right, the distance it is moved is also
        apportioned to smaller, interior subtrees, creating a pleasing
        aesthetic placement.
        """
        log.debug("Apportion node: {}, level: {}".format(node, level))
        left_most = self._get_node(node.first_child)
        neighbor = left_most.left_neighbor
        compare_depth = 1
        depth_to_stop = self.max_depth - level

        while left_most and neighbor and compare_depth <= depth_to_stop:
            # Compute the location of leftmost and where it should be with respect to neighbor
            left_mod_sum = 0
            right_mod_sum = 0
            ancestor_left_most = left_most
            ancestor_neighbor = neighbor
            for i in range(compare_depth):
                ancestor_left_most = self._get_node(ancestor_left_most.parent)
                ancestor_neighbor = self._get_node(ancestor_neighbor.parent)
                right_mod_sum += ancestor_left_most.modifier
                left_mod_sum += ancestor_neighbor.modifier
            # Find the move distance and apply it to node's sub-tree
            # Add appropriate portions to smaller interior sub-trees
            move_distance = (neighbor.prelim + left_mod_sum + self.subtree_separation + self.node_size) - (
                left_most.prelim + right_mod_sum
            )
            log.debug(
                "Move Distance = ({} + {} + {} + {}) - ({} + {}) = {}".format(
                    neighbor.prelim,
                    left_mod_sum,
                    self.subtree_separation,
                    self.node_size,
                    left_most.prelim,
                    right_mod_sum,
                    move_distance,
                )
            )
            if move_distance > 0:
                # Count interior sibling sub-trees in left siblings
                tmp = node
                left_siblings = 0
                while tmp and tmp != ancestor_neighbor:
                    left_siblings += 1
                    tmp = self._get_node(tmp.left_sibling)
                if tmp:
                    # Apply portions to appropriate left sibling sub-trees
                    portion = move_distance / left_siblings
                    tmp = node
                    # NB: this line is wrong in the original paper as it is missing the negation
                    # and without it, the move distances are not applied correctly to all subtrees.
                    while tmp != ancestor_neighbor:
                        log.debug("Applying move distance: {} to node: {}".format(move_distance, tmp))
                        tmp.prelim += move_distance
                        tmp.modifier += move_distance
                        move_distance -= portion
                        tmp = self._get_node(tmp.left_sibling)
                else:
                    # No need to move anything
                    # Needs to be done by an ancestor b/c ancestor neighbor and leftmost are not siblings
                    return
            # Determine the leftmost descendant of node at the next
            # lower level to compare its positioning against that of its
            # neighbor.
            compare_depth += 1
            if left_most.is_leaf:
                left_most = self._get_leftmost(node, 0, compare_depth)
            else:
                left_most = self._get_node(left_most.first_child)

            # NB: the original paper does not specify updating the neighbor, but this is
            # absolutely necessary to ensure that the neighbor stays in sync level-wise with
            # the leftmost node we are processing on the next iteration of the while loop.
            neighbor = left_most and left_most.left_neighbor

    # Initialize the list of previous nodes at each level.
    def _init_prev_node_list(self):
        # Start with the node at level 0 - the apex of the tree
        tmp = self._level_zero_ptr
        while tmp:
            tmp.prev_node = None
            tmp = tmp.next_level

    # Get the previous node at the given level
    def _get_prev_node(self, level):
        # Start with the node at level 0 - the apex of the tree
        tmp = self._level_zero_ptr
        i = 0
        while tmp:
            if i == level:
                return tmp.prev_node
            tmp = tmp.next_level
            i += 1
        return None

    # Internal class used to track previous progress
    class _NodeTracker:
        def __init__(self, prev_node=None, next_level=None):
            self.prev_node = prev_node
            self.next_level = next_level

    # Set an element in the list tracking previous nodes.
    def _set_prev_node(self, level, node):
        if not self._level_zero_ptr:
            self._level_zero_ptr = self._NodeTracker()
            self._level_zero_ptr.prev_node = node
            self._level_zero_ptr.next_level = None
            return

        # Start with the node at level 0 - the apex of the tree
        tmp = self._level_zero_ptr
        i = 0
        while tmp:
            if i == level:
                # At this level, replace the existing list element with
                # the given node
                tmp.prev_node = node
                return
            elif tmp.next_level is None:
                # There isn't a list element yet at this level, so
                # add one. The following instructions prepare the
                # list element at the next level, not at this one.
                new_node = self._NodeTracker()
                new_node.prev_node = None
                new_node.next_level = None
                tmp.next_level = new_node
            # Prepare to move to the next level, to look again.
            tmp = tmp.next_level
            i += 1

    def _check_extents_range(self, x, y):
        """Verifies that the passed x and y coordinates are within the coordinate system
        being used for drawing (if boundaries are set during configuration).
        """
        if x < self.min_x or x > self.max_x:
            raise exceptions.TreeOutOfCoordinateRange(
                "x: {} is beyond range configured: min: {}, max: {}".format(x, self.min_x, self.max_x)
            )
        if y < self.min_y or y > self.max_y:
            raise exceptions.TreeOutOfCoordinateRange(
                "y: {} is beyond range configured: min: {}, max: {}".format(y, self.min_y, self.max_y)
            )

    def _first_walk(self, node, level):
        """In this first postorder walk, every node of the tree is assigned a preliminary
        x-coordinate (node.prelim). In addition, internal nodes are given modifiers,
        which will be used to move their offspring to the right (node.modifier).
        """
        # Set pointer to previous node at this level
        node.left_neighbor = self._get_prev_node(level)
        # Update the previous node
        self._set_prev_node(level, node)
        # Set default modifier value
        node.modifier = 0
        log.debug("First walk, node: {}".format(node))
        if node.is_leaf or level == self.max_depth:
            if node.has_left_sibling():
                # Determine the preliminary x-coordinate
                node.prelim = self._get_node(node.left_sibling).prelim + self.sibling_separation + self.node_size
            else:
                # No sibling on left to worry about
                node.prelim = 0
        else:
            # This node is not a leaf, so call this recursively for each of its offspring
            left_most = right_most = self._get_node(node.first_child)
            self._first_walk(left_most, level + 1)
            while right_most.has_right_sibling():
                right_most = self._get_node(right_most.right_sibling)
                self._first_walk(right_most, level + 1)
            midpoint = (left_most.prelim + right_most.prelim) / 2
            if node.has_left_sibling():
                node.prelim = self._get_node(node.left_sibling).prelim + self.sibling_separation + self.node_size
                node.modifier = node.prelim - midpoint
                self._apportion(node, level)
            else:
                node.prelim = midpoint

    def _second_walk(self, node, level, mod_sum):
        """During a second preorder walk, each node is given a final x-coordinate
        by summing its preliminary x-coordinate and the modifiers of all the node's
        ancestors. The y-coordinate depends on the height of the tree. If the actual
        position of an interior node is right of its preliminary place, the subtree rooted
        at the node must be moved right to center the children around the parent. Rather than
        immediately readjust all the nodes in the subtree, each node remembers the distance to
        the provisional place in a modifier field (node.modifier).
        In this second pass down the tree, modifiers are accumulated and applied to every node.
        """
        if level > self.max_depth:
            raise exceptions.MaxDepthExceeded(
                "node: {} is at level: {}, which is greater than configured max depth: {}".format(
                    node.id, level, self.max_depth
                )
            )
        x_tmp = self._x_top_adj + node.prelim + mod_sum
        y_tmp = self._y_top_adj + (level * self.level_separation)
        # Check if tree is out of draw range based on tmp coordinates
        self._check_extents_range(x_tmp, y_tmp)

        log.debug("Second walk, node: {}".format(node))
        node.point = Point(x_tmp, y_tmp)
        if node.has_child():
            # Apply the modifier value to all offspring
            self._second_walk(self._get_node(node.first_child), level + 1, mod_sum + node.modifier)
        if node.has_right_sibling():
            self._second_walk(self._get_node(node.right_sibling), level, mod_sum)
        return

    def _get_node(self, node_id: str) -> Optional[_InternalNode]:
        if not node_id:
            return None
        if node_id not in self._tree:
            raise exceptions.NodeDoesNotExist("node ID: {}".format(node_id))
        return self._tree[node_id]

    def _validate_tree(self):
        no_parent_node_ids = []
        for node_id, node in self._tree.items():
            if node.is_leaf and (node.first_child or node.has_child()):
                raise exceptions.InvalidTree("leaf node cannot also have child: {}".format(node.id))
            if node.has_child() and not node.first_child:
                raise exceptions.InvalidTree("parent node must have child: {}".format(node.id))
            if node.parent is None:
                no_parent_node_ids.append(node.id)

            # Ensure all IDs exist in tree
            if node.id not in self._tree:
                raise exceptions.InvalidTree("node ID not in tree: {}".format(node.id))
            if node.parent and node.parent not in self._tree:
                raise exceptions.InvalidTree("parent ID not in tree for node: {}".format(node.id))
            if node.left_sibling and node.left_sibling not in self._tree:
                raise exceptions.InvalidTree("left sibling ID not in tree for node: {}".format(node.id))
            if node.right_sibling and node.right_sibling not in self._tree:
                raise exceptions.InvalidTree("right sibling ID not in tree for node: {}".format(node.id))
            if node.first_child and node.first_child not in self._tree:
                raise exceptions.InvalidTree("first child ID not in tree for node: {}".format(node.id))

            # Ensure siblings are consistent
            if node.has_left_sibling():
                left_sibling = self._tree[node.left_sibling]
                if left_sibling.right_sibling != node.id:
                    raise exceptions.InvalidTree("left sibling discrepancy: {}".format(node.id))
            if node.has_right_sibling():
                right_sibling = self._tree[node.right_sibling]
                if right_sibling.left_sibling != node.id:
                    raise exceptions.InvalidTree("right sibling discrepancy: {}".format(node.id))

            # Ensure parent child is consistent
            if node.has_child():
                first_child = self._tree[node.first_child]
                if first_child.parent != node.id:
                    raise exceptions.InvalidTree("first child discrepancy: {}".format(node.id))

        # Ensure only one root node is missing parent and set parent if valid
        if len(no_parent_node_ids) != 1:
            raise exceptions.InvalidTree("invalid number of nodes with no parent: {}".format(no_parent_node_ids))
        else:
            self._root_node_id = no_parent_node_ids[0]

    def populate_tree(self, nodes: Set[Node]):
        """This method populates the tree with the given set of nodes.
        Note: this merely establishes the set of nodes to process and validates the tree state.
        Node positions will not be updated until 'position_tree' is called.
        """
        for node in nodes:
            self._tree[node.id] = self._InternalNode(node)
        self._validate_tree()

    def position_tree(self):
        """This method determines the coordinates for each node in a tree.
        This assumes that the x and y coordinates of the apex node are already set as desired,
        since the tree underneath it will be positioned with respect to those coordinates.

        Tree repositioning is left decoupled from adding or removing nodes to allow for those actions
        to be done in bulk without incurring the costs of repositioning.
        """
        if len(self._tree) == 0:
            raise exceptions.InvalidTree("empty tree; tree must be populated before positioning")

        root = self._get_node(self._root_node_id)
        if not root:
            raise exceptions.InvalidTree("no root node found")

        self._init_prev_node_list()

        # Set preliminary positioning with postorder walk
        self._first_walk(root, 0)

        # Adjust all nodes with respect to root
        self._x_top_adj = root.point.x - root.prelim
        self._y_top_adj = root.point.y
        log.debug("Adjustments: x_top_adj: {}, y_top_adj: {}".format(self._x_top_adj, self._y_top_adj))

        # Set final positioning with preorder walk
        self._second_walk(root, 0, 0)

    def get_position(self, node_id: str) -> Point:
        """This method returns a Point(x, y) representation of the position for the given node.
        Note: if nodes have been added or removed, the position will only be updated once 'position_tree'
        is called. In other words, this call should come after a call to 'position_tree'.

        Example usage:
        point = tree.get_position(node_id)
        x_position = point.x
        y_position = point.y
        """
        if len(self._tree) == 0:
            raise exceptions.InvalidTree("empty tree; tree must be populated before positioning")

        node = self._get_node(node_id)
        return node.point
