"""Small, deterministic regex simplifications."""

from __future__ import annotations

from engine.regex.ast import Concat, Empty, Epsilon, Node, Star, Union
from engine.regex.derivative import nullable
from engine.regex.printer import to_string


def simplify(node: Node) -> Node:
    """Simplify bottom-up to a fixpoint; output is correct but not guaranteed minimal or readable."""
    previous: Node | None = None
    current = node
    while current != previous:
        previous = current
        current = _simplify_once(current)
    return current


def _simplify_once(node: Node) -> Node:
    if isinstance(node, (Empty, Epsilon)):
        return node
    if isinstance(node, Star):
        inner = _simplify_once(node.inner)
        if isinstance(inner, (Empty, Epsilon)):
            return Epsilon()
        if isinstance(inner, Star):
            return inner
        return Star(inner)
    if isinstance(node, Concat):
        left, right = _simplify_once(node.left), _simplify_once(node.right)
        if isinstance(left, Empty) or isinstance(right, Empty):
            return Empty()
        if isinstance(left, Epsilon):
            return right
        if isinstance(right, Epsilon):
            return left
        return Concat(left, right)
    if not isinstance(node, Union):
        return node
    left, right = _simplify_once(node.left), _simplify_once(node.right)
    values = _flatten_union(left) + _flatten_union(right)
    values = [value for value in values if not isinstance(value, Empty)]
    if not values:
        return Empty()
    if len(values) > 1:
        values = [value for value in values if not (isinstance(value, Epsilon) and any(nullable(v) for v in values if v != value))]
    unique = {to_string(value): value for value in values}
    ordered = [unique[key] for key in sorted(unique)]
    result = ordered[0]
    for value in ordered[1:]:
        result = Union(result, value)
    return result


def _flatten_union(node: Node) -> list[Node]:
    if isinstance(node, Union):
        return _flatten_union(node.left) + _flatten_union(node.right)
    return [node]
