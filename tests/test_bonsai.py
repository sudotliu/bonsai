import pytest
from typing import DefaultDict, List
from collections import defaultdict

from bonsai.exceptions import InvalidTree, CannotPruneRoot

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
    
def test_bonsai_add_leaf():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    bonsai.add_leaf("F", "B")
    assert bonsai.list_nodes() == [
        Node(id="A", pos=Point(0, 0), _is_leaf=False),
        Node(id="B", pos=Point(-150.0, 275), _is_leaf=False),
        Node(id="C", pos=Point(150.0, 275), _is_leaf=True),
        Node(id="D", pos=Point(-450.0, 550), _is_leaf=True),
        Node(id="E", pos=Point(-150.0, 550), _is_leaf=True),
        Node(id="F", pos=Point(150.0, 550), _is_leaf=True),
    ]

def test_bonsai_prune_leaf():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    bonsai.prune("E")
    assert bonsai.list_nodes() == [
        Node(id="A", pos=Point(0, 0), _is_leaf=False),
        Node(id="B", pos=Point(-150.0, 275), _is_leaf=False),
        Node(id="C", pos=Point(150.0, 275), _is_leaf=True),
        Node(id="D", pos=Point(-150.0, 550), _is_leaf=True),
    ]

def test_bonsai_prune_subtree():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    bonsai.prune("B")
    assert bonsai.list_nodes() == [
        Node(id="A", pos=Point(0, 0), _is_leaf=False),
        Node(id="C", pos=Point(0.0, 275), _is_leaf=True),
    ]

def test_bonsai_add_leaf_invalid():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    with pytest.raises(ValueError):
        bonsai.add_leaf("B", "A")

def test_bonsai_no_nodes():
    tree = defaultdict(list)
    with pytest.raises(InvalidTree):
        bonsai = Bonsai(tree)
   
def test_bonsai_add_leaf_and_prune_to_root():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    bonsai.add_leaf("F", "B")
    bonsai.prune("B")
    bonsai.prune("C")
    assert bonsai.list_nodes() == [
        Node(id="A", pos=Point(0, 0), _is_leaf=False),
    ]

def test_bonsai_prune_to_root_and_add_leaf():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    bonsai.prune("B")
    bonsai.prune("C")
    bonsai.add_leaf("B", "A")
    assert bonsai.list_nodes() == [
        Node(id="A", pos=Point(0, 0), _is_leaf=False),
        Node(id="B", pos=Point(0.0, 275), _is_leaf=True),
    ]

def test_bonsai_prune_root():
    tree = defaultdict(list)
    tree["A"] = [Node(id="B", pos=Point(0, 0)), Node(id="C", pos=Point(1, 0))]
    tree["B"] = [Node(id="D", pos=Point(0, 1)), Node(id="E", pos=Point(1, 1))]
    bonsai = Bonsai(tree)
    with pytest.raises(CannotPruneRoot):
        bonsai.prune("A")
 