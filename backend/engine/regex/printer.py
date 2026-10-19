"""Canonical printers for regex ASTs."""

from __future__ import annotations

from engine.regex.ast import Empty, Epsilon, Node, Star, Symbol, Union


def to_string(node: Node) -> str:
    """Print an AST with minimal grouping and escaped literal symbols."""
    return _print(node, 0, False)


def _print(node: Node, parent_precedence: int, right_same: bool) -> str:
    if isinstance(node, Empty):
        result = "∅"
        precedence = 4
    elif isinstance(node, Epsilon):
        result = "ε"
        precedence = 4
    elif isinstance(node, Symbol):
        result = _escape(node.char)
        precedence = 4
    elif isinstance(node, Star):
        result = f"{_print(node.inner, 3, False)}*"
        precedence = 3
    elif isinstance(node, Union):
        result = f"{_print(node.left, 1, False)}|{_print(node.right, 1, True)}"
        precedence = 1
    else:
        result = f"{_print(node.left, 2, False)}{_print(node.right, 2, True)}"
        precedence = 2
    if precedence < parent_precedence or (right_same and precedence == parent_precedence):
        return f"({result})"
    return result


def _escape(char: str) -> str:
    if char in {"\\", "|", "*", "+", "?", "(", ")", "ε", "∅"} or char.isspace():
        return f"\\{char}"
    if char in ".[]{}^$":
        return f"\\{char}"
    return char
