"""Reachable-pair product construction."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable

from engine.automata.model import DFA
from engine.steps import Step
from engine.util import natural_sorted


def product(
    a: DFA, b: DFA, accept: Callable[[bool, bool], bool]
) -> tuple[DFA, list[Step]]:
    """Build the reachable product DFA with BFS state naming."""
    alphabet = a.alphabet | b.alphabet
    start_pair = (a.start, b.start)
    names = {start_pair: "p0"}
    queue = deque([start_pair])
    transitions: dict[tuple[str, str], str] = {}
    accepting: set[str] = set()
    steps: list[Step] = []
    while queue:
        pair = queue.popleft()
        name = names[pair]
        if accept(pair[0] in a.accepting, pair[1] in b.accepting):
            accepting.add(name)
        moves = {}
        for symbol in natural_sorted(alphabet):
            target = (a.transitions[(pair[0], symbol)], b.transitions[(pair[1], symbol)])
            if target not in names:
                names[target] = f"p{len(names)}"
                queue.append(target)
            transitions[(name, symbol)] = names[target]
            moves[symbol] = names[target]
        steps.append(Step(
            f"Explore {name}",
            "Explore one reachable pair of component states.",
            {"state": name, "pair": list(pair), "moves": moves},
        ))
    result = DFA(
        frozenset(names.values()), alphabet, "p0", frozenset(accepting), transitions,
        {name: pair for pair, name in names.items()},
    )
    result.validate()
    return result, steps
