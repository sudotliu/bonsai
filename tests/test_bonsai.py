import pytest
from typing import DefaultDict, List
from collections import defaultdict

from .context import Node, Point, Bonsai


def test_bonsai_initialization():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    assert bonsai.list_nodes() == [
        Node(id="A", pos=Point(0, 0), _is_leaf=False),
        Node(id="B", pos=Point(-150.0, 275), _is_leaf=False),
        Node(id="C", pos=Point(150.0, 275), _is_leaf=True),
        Node(id="D", pos=Point(-300.0, 550), _is_leaf=True),
        Node(id="E", pos=Point(0.0, 550), _is_leaf=True),
    ]
    
# def test_bonsai_add_leaf():
#     tree = defaultdict(list)
#     tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
#     tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
#     bonsai = Bonsai(tree)
#     bonsai.add_leaf("F", "B")
#     assert bonsai.list_nodes() == [
#         Node(id="A", pos=Point(0, 0), _is_leaf=False),
#         Node(id="B", pos=Point(-150.0, 275), _is_leaf=False),
#         Node(id="D", pos=Point(-300.0, 550), _is_leaf=True),
#         Node(id="E", pos=Point(0.0, 550), _is_leaf=True),
#         Node(id="F", pos=Point(150.0, 550), _is_leaf=True),
#         Node(id="C", pos=Point(150.0, 275), _is_leaf=True),
#     ]

# def test_bonsai_prune():
#     tree = {
#         "A": [Node(id="B", pos=(0, 0)), Node(id="C", pos=(1, 0))],
#         "B": [Node(id="D", pos=(0, 1)), Node(id="E", pos=(1, 1))],
#     }
#     bonsai = Bonsai(tree)
#     bonsai.prune("B", "A")
#     assert bonsai.list_nodes() == [
#         Node(id="A", pos=(0, 0), _is_leaf=False),
#         Node(id="C", pos=(1, 0), _is_leaf=False),
#     ]

# def test_bonsai_invalid_tree():
#     tree = {
#         "A": [Node(id="B", pos=(0, 0)), Node(id="C", pos=(1, 0))],
#         "B": [Node(id="D", pos=(0, 1)), Node(id="E", pos=(1, 1))],
#     }
#     bonsai = Bonsai(tree)
#     with pytest.raises(ValueError):
#         bonsai.add_leaf("B", "A")

# def test_bonsai_no_nodes():
#     tree = {}
#     bonsai = Bonsai(tree)
#     with pytest.raises(ValueError):
#         bonsai._root_id()
    