from __future__ import annotations
from typing import List


class ASTNode:
    """
    Generic node in an abstract syntax tree (AST) or standardized tree (ST).
    """

    __slots__ = ("value", "children", "level")

    def __init__(self, value: str) -> None:
        self.value: str = value
        self.children: List[ASTNode] = []
        self.level: int = 0

    def add_child(self, child: ASTNode) -> None:
        self.children.append(child)

    def __repr__(self) -> str:
        return f"ASTNode({self.value!r}, children={len(self.children)})"


def preorder_traversal(root: ASTNode) -> None:
    """
    Prints the tree: each node on its own line, prefixed by '.' * level.
    """
    def _dfs(node: ASTNode) -> None:
        print("." * node.level + node.value)
        for child in node.children:
            child.level = node.level + 1
            _dfs(child)

    if root:
        _dfs(root)
