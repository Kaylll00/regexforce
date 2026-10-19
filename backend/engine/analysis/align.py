"""Alphabet alignment for DFA operations."""

from __future__ import annotations

from collections.abc import Iterable

from engine.automata.dfa_ops import complete_dfa
from engine.automata.model import DFA


def align(a: DFA, b: DFA, extra_alphabet: Iterable[str] | None = None) -> tuple[DFA, DFA]:
    """Complete two DFAs over the same combined alphabet."""
    alphabet = a.alphabet | b.alphabet | frozenset(extra_alphabet or ())
    left, _ = complete_dfa(a, alphabet)
    right, _ = complete_dfa(b, alphabet)
    return left, right
