"""Immutable regular grammar data structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Production:
    """One grammar production body."""

    head: str
    body: tuple[str, ...]


@dataclass(frozen=True)
class Grammar:
    """A regular grammar and its linearity."""

    start: str
    productions: tuple[Production, ...]
    kind: str
