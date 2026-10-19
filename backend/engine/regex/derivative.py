"""Brzozowski derivatives used as an independent regex reference matcher."""

from __future__ import annotations

from engine.regex.ast import Concat, Empty, Epsilon, Node, Star, Symbol, Union


def nullable(node: Node) -> bool:
    """Return whether an expression accepts the empty string."""
    if isinstance(node, Epsilon):
        return True
    if isinstance(node, (Empty, Symbol)):
        return False
    if isinstance(node, Star):
        return True
    if isinstance(node, Union):
        return nullable(node.left) or nullable(node.right)
    return nullable(node.left) and nullable(node.right)


def derive(node: Node, ch: str) -> Node:
    """Compute the Brzozowski derivative with respect to one character."""
    if isinstance(node, (Empty, Epsilon)):
        return Empty()
    if isinstance(node, Symbol):
        return Epsilon() if node.char == ch else Empty()
    if isinstance(node, Union):
        return _union(derive(node.left, ch), derive(node.right, ch))
    if isinstance(node, Concat):
        first = _concat(derive(node.left, ch), node.right)
        if nullable(node.left):
            return _union(first, derive(node.right, ch))
        return first
    return _concat(derive(node.inner, ch), node)


def matches(node: Node, s: str) -> bool:
    """Match a string by repeatedly applying regex derivatives."""
    current = node
    for ch in s:
        current = derive(current, ch)
    return nullable(current)


def _union(left: Node, right: Node) -> Node:
    if isinstance(left, Empty):
        return right
    if isinstance(right, Empty) or left == right:
        return left
    return Union(left, right)


def _concat(left: Node, right: Node) -> Node:
    if isinstance(left, Empty) or isinstance(right, Empty):
        return Empty()
    if isinstance(left, Epsilon):
        return right
    if isinstance(right, Epsilon):
        return left
    return Concat(left, right)
