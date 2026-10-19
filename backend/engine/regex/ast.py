"""Immutable abstract syntax trees for classical regular expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from engine.errors import RegexSyntaxError


@dataclass(frozen=True)
class Empty:
    """The empty language."""


@dataclass(frozen=True)
class Epsilon:
    """The language containing the empty string."""


@dataclass(frozen=True)
class Symbol:
    """A single literal symbol."""

    char: str

    def __post_init__(self) -> None:
        if len(self.char) != 1 or self.char in {"ε", "∅"}:
            raise ValueError("Symbol must be one character other than ε or ∅.")


@dataclass(frozen=True)
class Union:
    """The union of two expressions."""

    left: Node
    right: Node


@dataclass(frozen=True)
class Concat:
    """The concatenation of two expressions."""

    left: Node
    right: Node


@dataclass(frozen=True)
class Star:
    """The Kleene closure of an expression."""

    inner: Node


Node: TypeAlias = Empty | Epsilon | Symbol | Union | Concat | Star


def alphabet_of(node: Node) -> frozenset[str]:
    """Return the literal alphabet occurring in an expression."""
    if isinstance(node, Symbol):
        return frozenset({node.char})
    if isinstance(node, (Empty, Epsilon)):
        return frozenset()
    if isinstance(node, Star):
        return alphabet_of(node.inner)
    return alphabet_of(node.left) | alphabet_of(node.right)


def to_dict(node: Node) -> dict[str, object]:
    """Serialize an expression tree to its JSON representation."""
    if isinstance(node, Empty):
        return {"type": "empty"}
    if isinstance(node, Epsilon):
        return {"type": "epsilon"}
    if isinstance(node, Symbol):
        return {"type": "symbol", "char": node.char}
    if isinstance(node, Union):
        return {"type": "union", "left": to_dict(node.left), "right": to_dict(node.right)}
    if isinstance(node, Concat):
        return {"type": "concat", "left": to_dict(node.left), "right": to_dict(node.right)}
    return {"type": "star", "inner": to_dict(node.inner)}


def from_dict(data: dict[str, object]) -> Node:
    """Deserialize a JSON expression representation."""
    kind = data.get("type")
    if kind == "empty":
        return Empty()
    if kind == "epsilon":
        return Epsilon()
    if kind == "symbol":
        char = data.get("char")
        if not isinstance(char, str):
            raise RegexSyntaxError("A symbol requires a character.")
        return Symbol(char)
    if kind in {"union", "concat"}:
        left = data.get("left")
        right = data.get("right")
        if not isinstance(left, dict) or not isinstance(right, dict):
            raise RegexSyntaxError(f"{kind} requires left and right operands.")
        cls = Union if kind == "union" else Concat
        return cls(from_dict(left), from_dict(right))
    if kind == "star":
        inner = data.get("inner")
        if not isinstance(inner, dict):
            raise RegexSyntaxError("star requires an inner expression.")
        return Star(from_dict(inner))
    raise RegexSyntaxError("Unknown regex AST node type.")
