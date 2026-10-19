"""Bounded derivation search for regular grammars."""

from __future__ import annotations

from collections import deque

from engine.grammar.model import Grammar
from engine.steps import Step


def find_derivation(grammar: Grammar, string: str) -> tuple[list[str] | None, list[Step]]:
    """Find a derivation with visited forms so unit-production cycles terminate."""
    queue: deque[tuple[str, list[str], list[Step]]] = deque([
        (grammar.start, [grammar.start], [])
    ])
    visited = {grammar.start}
    while queue:
        form, forms, steps = queue.popleft()
        if form == string:
            return forms, [
                *steps,
                Step("Linear derivation", "Because the grammar is linear, this is both leftmost and rightmost.", {}),
            ]
        position = next((index for index, char in enumerate(form) if char.isupper()), None)
        if position is None:
            continue
        for production in grammar.productions:
            if production.head != form[position]:
                continue
            replacement = "".join(production.body).replace("ε", "")
            candidate = form[:position] + replacement + form[position + 1:]
            if grammar.kind == "right-linear":
                if not string.startswith(candidate[:position]):
                    continue
            else:
                if not string.endswith(candidate[position + len(replacement):]):
                    continue
            terminal_count = len(candidate.replace(next((c for c in candidate if c.isupper()), ""), ""))
            if terminal_count > len(string):
                continue
            if candidate not in visited:
                visited.add(candidate)
                step = Step(
                    "Apply production",
                    f"Apply {production.head} -> {''.join(production.body)}.",
                    {"production": f"{production.head} -> {''.join(production.body)}", "form": candidate},
                )
                queue.append((candidate, [*forms, candidate], [*steps, step]))
    return None, [Step("No derivation", "No sentential-form path reaches the requested string.", {})]
