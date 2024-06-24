"""
Custom exceptions for tree positioning failure modes.
"""

__all__ = [
    "InvalidTreeConfiguration",
    "InvalidTree",
    "NodeDoesNotExist",
    "TreeOutOfCoordinateRange",
    "MaxDepthExceeded"
]

class InvalidTreeConfiguration(Exception):
    """Raised when tree configuration validation detects invalid values"""

class InvalidTree(Exception):
    """Raised any time the state of the tree is invalid e.g. multiple roots"""

class NodeDoesNotExist(Exception):
    """Raised when tree configuration validation detects invalid values"""

class TreeOutOfCoordinateRange(Exception):
    """Raised any time the positioning of the tree would cause it to exceed the specified range"""

class MaxDepthExceeded(Exception):
    """Raised tree level being positioned has exceeded the configured max depth """
