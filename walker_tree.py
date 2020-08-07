"""
Python implementation of Walker tree node positioning algorithm.
http://www.cs.unc.edu/techreports/89-034.pdf
"""

from typing import Optional

# GLOBALS
# The algorithm maintains a list of the previous node at each level i.e. the adjacent neighbor to the left.
# LEVEL_ZERO_PTR is a pointer to the first entry in this list.
LEVEL_ZERO_PTR = None
# Fixed distances used in the final walk of the tree to determine the absolute coordinates
# of a node with respect to the apex node of the tree.
X_TOP_ADJ = 0
Y_TOP_ADJ = 0

# The minimum distance between adjacent siblings of the tree
SIBLING_SEPARATION = 50
# The minimum distance between adjacent subtrees of a tree.
# For proper aesthetics, this value is normally somewhat larger than SIBLING_SEPARATION.
SUBTREE_SEPARATION = 100
# The fixed distance between adjacent levels of the tree.
# Used in determining the y-coordinate of a node being positioned.
LEVEL_SEPARATION = 50
# The maximum number of levels in the tree to be positioned.
# If all levels are to be positioned, set this value to positive infinity (or an appropriate numerical value).
MAX_DEPTH = 100
# The width of a node to be accounted for when calculating positioning.
# For nodes of different sizes refer to original algorithm and use the MEAN_NODE_SIZE calculations.
NODE_SIZE = 300


class Node:
    def __init__(self, value, is_leaf, left_sibling, right_sibling, parent, first_child):
        # The current node's preliminary x-coordinate
        self.prelim = 0
        # The current node's modifier value
        self.modifier = 0
        # The current node's nearest neighbor to the left, at the same level
        self.left_neighbor = None
        # Position coordinates of the node
        self.x = 0
        self.y = 0
        # Stored values upon building the tree
        self.value = value
        self.is_leaf = is_leaf
        self.left_sibling = left_sibling
        self.right_sibling = right_sibling
        self.parent = parent
        self.first_child = first_child

    def has_child(self):
        return not self.is_leaf

    def has_left_sibling(self):
        return self.left_sibling is not None

    def has_right_sibling(self):
        return self.right_sibling is not None


DB = {
    'A': Node(value='A', is_leaf=True, left_sibling=None, right_sibling='D', parent='E', first_child=None),
    'B': Node(value='B', is_leaf=True, left_sibling=None, right_sibling='C', parent='D', first_child=None),
    'C': Node(value='C', is_leaf=True, left_sibling='B', right_sibling=None, parent='D', first_child=None),
    'D': Node(value='D', is_leaf=False, left_sibling='A', right_sibling=None, parent='E', first_child='B'),
    'E': Node(value='E', is_leaf=False, left_sibling=None, right_sibling='F', parent='O', first_child='A'),
    'F': Node(value='F', is_leaf=True, left_sibling='E', right_sibling='N', parent='O', first_child=None),
    'G': Node(value='G', is_leaf=True, left_sibling=None, right_sibling='M', parent='N', first_child=None),
    'H': Node(value='H', is_leaf=True, left_sibling=None, right_sibling='I', parent='M', first_child=None),
    'I': Node(value='I', is_leaf=True, left_sibling='H', right_sibling='J', parent='M', first_child=None),
    'J': Node(value='J', is_leaf=True, left_sibling='I', right_sibling='K', parent='M', first_child=None),
    'K': Node(value='K', is_leaf=True, left_sibling='J', right_sibling='L', parent='M', first_child=None),
    'L': Node(value='L', is_leaf=True, left_sibling='K', right_sibling=None, parent='M', first_child=None),
    'M': Node(value='M', is_leaf=False, left_sibling='G', right_sibling=None, parent='N', first_child='H'),
    'N': Node(value='N', is_leaf=False, left_sibling='F', right_sibling=None, parent='O', first_child='G'),
    'O': Node(value='O', is_leaf=False, left_sibling=None, right_sibling=None, parent=None, first_child='E'),
}


def data(key):
    if not key:
        return None
    return DB[key]


# This function returns the leftmost descendant of a node at a given depth.
# This uses a postorder walk of the subtree under node, down to the level of depth.
# 'level' here is not the absolute tree level but the level below the node whose
# leftmost descendant is being found.
def get_leftmost(node, level, depth) -> Optional[Node]:
    if level >= depth:
        return node
    elif node.is_leaf:
        return None
    else:
        right_most = data(node.first_child)
        left_most = get_leftmost(right_most, level + 1, depth)
        # Do a postorder walk of the subtree below node
        while left_most and right_most.has_right_sibling():
            right_most = data(right_most.right_sibling)
            left_most = get_leftmost(right_most, level + 1, depth)
        return left_most


# Cleans up the positioning of small sibling subtrees.
# When moving a new subtree farther and farther to the right,
# gaps may open up among smaller subtrees that were previously
# sandwiched between larger subtrees. Thus, when moving the new,
# larger subtree to the right, the distance it is moved is also
# apportioned to smaller, interior subtrees, creating a pleasing
# aesthetic placement.
def apportion(node, level):
    left_most = data(node.first_child)
    neighbor = left_most.left_neighbor
    compare_depth = 1
    depth_to_stop = MAX_DEPTH - level

    while left_most and neighbor and compare_depth <= depth_to_stop:
        # Compute the location of leftmost and where it should be with respect to neighbor
        left_mod_sum = 0
        right_mod_sum = 0
        ancestor_left_most = left_most
        ancestor_neighbor = neighbor
        for i in range(compare_depth):
            ancestor_left_most = data(ancestor_left_most.parent)
            ancestor_neighbor = data(ancestor_neighbor.parent)
            right_mod_sum += ancestor_left_most.modifier
            left_mod_sum += ancestor_neighbor.modifier
        # Find the move distance and apply it to node's sub-tree
        # Add appropriate portions to smaller interior sub-trees
        move_distance = (neighbor.prelim + left_mod_sum + SUBTREE_SEPARATION + NODE_SIZE) - \
                        (left_most.prelim + right_mod_sum)
        if move_distance:
            # Count interior sibling sub-trees in left siblings
            tmp = node
            left_siblings = 0
            while tmp and tmp != ancestor_neighbor:
                left_siblings += 1
                tmp = data(tmp.left_sibling)
            if tmp:
                # Apply portions to appropriate left sibling sub-trees
                portion = move_distance / left_siblings
                tmp = node
                while tmp == ancestor_neighbor:
                    tmp.prelim += move_distance
                    tmp.modifier += move_distance
                    move_distance -= portion
                    tmp = data(tmp.left_sibling)
            else:
                # No need to move anything
                # Needs to be done by an ancestor b/c ancestor neighbor and leftmost are not siblings
                return
        # Determine the leftmost descendant of node at the next
        # lower level to compare its positioning against that of its
        # neighbor.
        compare_depth += 1
        if left_most.is_leaf:
            left_most = get_leftmost(node, 0, compare_depth)
        else:
            left_most = data(left_most.first_child)


# Initialize the list of previous nodes at each level.
def init_prev_node_list():
    # Start with the node at level 0 - the apex of the tree
    tmp = LEVEL_ZERO_PTR
    while tmp:
        tmp.prev_node = None
        tmp = tmp.next_level


# Get the previous node at the given level
def get_prev_node(level):
    # Start with the node at level 0 - the apex of the tree
    tmp = LEVEL_ZERO_PTR
    i = 0
    while tmp:
        if i == level:
            return tmp.prev_node
        tmp = tmp.next_level
        i += 1
    # Otherwise, there was no node at the specific level
    return None


class NodeTracker:
    def __init__(self, prev_node=None, next_level=None):
        self.prev_node = prev_node
        self.next_level = next_level


# Set an element in the list tracking previous nodes.
def set_prev_node(level, node):
    global LEVEL_ZERO_PTR
    if not LEVEL_ZERO_PTR:
        LEVEL_ZERO_PTR = NodeTracker()
        LEVEL_ZERO_PTR.prev_node = node
        LEVEL_ZERO_PTR.next_level = None
        return

    # Start with the node at level 0 - the apex of the tree
    tmp = LEVEL_ZERO_PTR
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
            new_node = NodeTracker()
            new_node.prev_node = None
            new_node.next_level = None
            tmp.next_level = new_node
        # Prepare to move to the next level, to look again.
        tmp = tmp.next_level
        i += 1


# Verifies that the passed x- and y- coordinates are within the coordinate system
# being used for drawing.
def check_extents_range(x, y):
    # return x >= 0 and y >= 0
    return True


# In this first postorder walk, every node of the tree is assigned a preliminary
# x-coordinate (node.prelim). In addition, internal nodes are given modifiers,
# which will be used to move their offspring to the right (node.modifier).
def first_walk(node, level):
    # Set pointer to previous node at this level
    node.left_neighbor = get_prev_node(level)
    set_prev_node(level, node)  # this is now the previous
    node.modifier = 0  # set default modifier value
    print("First Walk Processing Node: {}, left neighbor: {}".format(
        node.value, node.left_neighbor and node.left_neighbor.value))
    if node.is_leaf or level == MAX_DEPTH:
        if node.has_left_sibling():
            # Determine the preliminary x-coordinate
            node.prelim = data(node.left_sibling).prelim + SIBLING_SEPARATION + NODE_SIZE
        else:
            # No sibling on left to worry about
            node.prelim = 0
    else:
        # This node is not a leaf, so call this recursively for each of its offspring
        left_most = right_most = data(node.first_child)
        first_walk(left_most, level + 1)
        while right_most.has_right_sibling():
            right_most = data(right_most.right_sibling)
            first_walk(right_most, level + 1)
        midpoint = (left_most.prelim + right_most.prelim) / 2
        if node.has_left_sibling():
            node.prelim = data(node.left_sibling).prelim + SIBLING_SEPARATION + NODE_SIZE
            node.modifier = node.prelim - midpoint
            apportion(node, level)
        else:
            node.prelim = midpoint


# During a second preorder walk, each node is given a final x-coordinate
# by summing its preliminary x-coordinate and the modifiers of all the node's
# ancestors. The y-coordinate depends on the height of the tree. If the actual
# position of an interior node is right of its preliminary place, the subtree rooted
# at the node must be moved right to center the children around the parent. Rather than
# immediately readjust all the nodes in the subtree, each node remembers the distance to
# the provisional place in a modifier field (node.modifier).
# In this second pass down the tree, modifiers are accumulated and applied to every node.
# Returns True if no errors, otherwise returns False.
def second_walk(node, level, mod_sum) -> bool:
    if level > MAX_DEPTH:
        return True
    x_tmp = X_TOP_ADJ + node.prelim + mod_sum
    y_tmp = Y_TOP_ADJ + (level * LEVEL_SEPARATION)
    # Check to see that tmp coordinates are of the proper size
    print("Second Walk Processing Node: {}, left neighbor: {}".format(
        node.value, node.left_neighbor and node.left_neighbor.value))
    if not check_extents_range(x_tmp, y_tmp):
        print("OUT OF RANGE")
        print(x_tmp)
        print(y_tmp)
        # Tree is out of draw range
        return False
    node.x = x_tmp
    node.y = y_tmp
    result = True
    if node.has_child():
        # Apply the modifier value to all offspring
        result = second_walk(data(node.first_child), level + 1, mod_sum + node.modifier)
    if result and node.has_right_sibling():
        # result = second_walk(data(node.right_sibling), level + 1, mod_sum)
        result = second_walk(data(node.right_sibling), level, mod_sum)
    return result


def _dump_nodes():
    nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
    print()
    for node in nodes:
        print("Node: {}, prelim: {}, mod: {}, x: {}, y: {}".format(
            node, data(node).prelim, data(node).modifier, data(node).x, data(node).y))


# This function determines the coordinates for each node in a tree. A pointer to the apex node
# of the tree is passed as input. This assumes that the x and y coordinates of the apex node are
# set as desired, since the tree underneath it will be positioned with respect to those coordinates.
# Returns True if no errors, otherwise returns False.
def position_tree(node: Node) -> bool:
    _dump_nodes()
    print("\nRunning positioning...\n")
    if not node:
        return True

    init_prev_node_list()

    # Set preliminary positioning with postorder walk
    print("First Walk")
    first_walk(node, 0)
    _dump_nodes()

    # Adjust all nodes with respect to root
    print("\nAdjusting coordinate offsets...\n")
    global X_TOP_ADJ
    X_TOP_ADJ = node.x - node.prelim
    print("X_TOP_ADJ: {}".format(X_TOP_ADJ))
    global Y_TOP_ADJ
    Y_TOP_ADJ = node.y
    print("Y_TOP_ADJ: {}".format(Y_TOP_ADJ))

    # Set final positioning with preorder walk
    print("Second Walk")
    result = second_walk(node, 0, 0)
    _dump_nodes()
    return result
