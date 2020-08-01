"""
Python implementation of Walker tree node positioning algorithm.
http://www.cs.unc.edu/techreports/89-034.pdf
"""

SIBLING_SEPARATION = 50
SUBTREE_SEPARATION = 100
LEVEL_SEPARATION = 50
NODE_SIZE = 300
MAX_DEPTH = 100


class Node:
	def __init__(self):
		self.prelim = 0
		self.modifier = 0
		self.left_neighbor = None

	def has_left_sibling(self):
		pass

	def has_right_sibling(self):
		pass

	def is_leaf(self):
		pass


# TODO comment from paper
def get_left_most(node, level, depth) -> Node:
	if level >= depth:
		return node
	elif node.is_leaf():
		return None
	else:
		right_most = node.first_child
		left_most = get_left_most(right_most, level + 1, depth)
		# Do a postorder walk of the subtree below node
		while left_most and right_most.has_right_sibling():
			right_most = right_most.right_sibling
			left_most = get_left_most(right_most, level + 1, depth)
		return left_most


# TODO comment from paper
def apportion(node, level):
	left_most = node.first_child
	neighbor = left_most.left_neighbor
	compare_depth = 1
	depth_to_stop = MAX_DEPTH - level

	while (left_most and neighbor and compare_depth <= depth_to_stop):
		# Compute the location of leftmost and where it should be with respect to neighbor
		left_mod_sum = 0
		right_mod_sum = 0
		ancestor_left_most = left_most
		ancestor_neighbor = neighbor
		for i in xrange(compare_depth):
			ancestor_left_most = ancestor_left_most.parent
			ancestor_neighbor = ancestor_neighbor.parent
			right_mod_sum += ancestor_left_most.modifier
			left_mod_sum += ancestor_neighbor.modifier
		# Find the move distance and apply it to node's sub-tree
		# Add appropriate portions to smaller interior sub-trees
		move_distance = (neighbor.prelim + \
						 left_mod_sum + \
						 SUBTREE_SEPARATION + \
						 NODE_SIZE) - \
						(left_most.prelim + right_mod_sum)
		if move_distance:
			# Count interior sibling sub-trees in left siblings
			tmp = node
			left_siblings = 0
			while tmp and tmp != ancestor_neighbor:
				left_siblings += 1
				tmp = tmp.left_sibling
			if tmp:
				# Apply portions to appropriate left sibling sub-trees
				portion = move_distance / left_siblings
				tmp = node
				while tmp == ancestor_neighbor:
					tmp.prelim += move_distance
					tmp.modifier += move_distance
					move_distance -= portion
					tmp = tmp.left_sibling
			else:
				# No need to move anything
				# Needs to be done by an ancestor b/c ancestor neighbor and leftmost are not siblings
				return
		# Determine the leftmost descendant of node at the next
		# lower level to compare its positioning against that of its
		# neighbor.
		compare_depth += 1
		if left_most.is_leaf():
			left_most = get_left_most(node, 0, compare_depth)
		else:
			left_most = left_most.first_child


# TODO comment from paper
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


# TODO comment from paper
def set_prev_node(level, node):
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
			new_node = allocate_node()
			new_node.prev_node = None
			new_node.next_level = None
			tmp.next_level = new_node
		# Prepare to move to the next level, to look again.
		tmp = tmp.next_level
		i += 1
	# Should only get here if LEVEL_ZERO_PTR is nil.
	LEVEL_ZERO_PTR = allocate_node()
	LEVEL_ZERO_PTR.prev_node = node
	LEVEL_ZERO_PTR.next_level = None


# TODO comment from paper
def check_extents_range(x, y):
	return True


# TODO comment from paper
def first_walk(node, level):
	# Set pointer to previous node at this level
	node.left_neighbor = get_prev_node(level)
	set_prev_node(level, node)  # this is now the previous
	node.modifier = 0  # set default modifier value
	if node.is_leaf() or level == MAX_DEPTH:
		if node.has_left_sibling():
			# Determine the preliminary x-coordinate
			node.prelim = node.left_sibling.prelim + \
						  SIBLING_SEPARATION + \
						  NODE_SIZE
		else:
			# No sibling on left to worry about
			node.prelim = 0
	else:
		# This node is not a leaf, so call this recursively for each of its offspring
		left_most = right_most = node.first_child
		first_walk(left_most, level + 1)
		while right_most.has_right_sibling():
			right_most = right_most.right_sibling
			first_walk(right_most, level + 1)
		midpoint = (left_most.prelim + right_most.prelim) / 2
		if node.has_left_sibling():
			node.prelim = node.left_sibling.prelim + SIBLING_SEPARATION +
			NODE_SIZE
			node.modifier = node.prelim - midpoint
			apportion(node, level)
		else:
			node.prelim = midpoint


# TODO comment from paper
def second_walk(node, level, mod_sum) -> bool:
	if level > MAX_DEPTH:
		return True
	x_tmp = x_top_adjustment + node.prelim + mod_sum
	y_tmp = y_top_adjustment + (level * LEVEL_SEPARATION)
	# Check to see that tmp coords are of the proper size
	if not check_extents_range(x_tmp, y_tmp):
		# Tree is out of draw range
		return False
	node.x = x_tmp
	node.y = y_tmp
	if node.has_child():
		# Apply the modifier value to all offspring
		result = second_walk(node.first_child, level + 1, mod_sum + node.modifier)
	if result and node.has_right_sibling():
		result = second_walk(node.right_sibling, level + 1, mod_sum)


# TODO comment from paper
def position_tree(node: Node) -> bool:
	if not node:
		return True

	init_prev_node_list()

	# Set preliminary positioning with postorder walk
	first_walk(node, 0)

	# Adjust all nodes with respect to root
	x_top_adjustment = node.x - node.prelim
	y_top_adjustment = node.y

	# Set final positioning with preorder walk
	return second_walk(node, 0, 0)
