"""Canonical grammar text rendering."""

from __future__ import annotations

from collections import defaultdict

from engine.grammar.model import Grammar


def grammar_to_text(grammar: Grammar) -> str:
    """Render productions grouped by their nonterminal head."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for production in grammar.productions:
        grouped[production.head].append("".join(production.body))
    return "\n".join(
        f"{head} -> " + " | ".join(grouped[head])
        for head in sorted(grouped)
    )
