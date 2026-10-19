"""Subset construction from NFAs to partial DFAs."""

from __future__ import annotations

from collections import deque

from engine.automata.model import DFA, NFA
from engine.automata.nfa_ops import epsilon_closure
from engine.errors import LimitError
from engine.steps import Step
from engine.util import cap_steps, natural_sorted


def nfa_to_dfa(nfa: NFA) -> tuple[DFA, list[Step]]:
    """Construct a partial DFA by breadth-first subset discovery."""
    start_subset = epsilon_closure(nfa, {nfa.start})
    subsets: list[frozenset[str]] = [start_subset]
    names = {start_subset: "d0"}
    queue: deque[frozenset[str]] = deque([start_subset])
    transitions: dict[tuple[str, str], str] = {}
    steps: list[Step] = []
    while queue:
        subset = queue.popleft()
        if len(subsets) > 2000:
            raise LimitError("Subset construction exceeded 2000 DFA states.")
        name = names[subset]
        moves: dict[str, str] = {}
        for symbol in natural_sorted(nfa.alphabet):
            moved = {
                target
                for state in subset
                for target in nfa.transitions.get((state, symbol), frozenset())
            }
            target_subset = epsilon_closure(nfa, moved)
            if not target_subset:
                continue
            if target_subset not in names:
                names[target_subset] = f"d{len(subsets)}"
                subsets.append(target_subset)
                queue.append(target_subset)
            transitions[(name, symbol)] = names[target_subset]
            moves[symbol] = names[target_subset]
        accepting = bool(subset & nfa.accepting)
        steps.append(Step(
            f"Discover {name}",
            f"Process the NFA subset represented by {name}.",
            {
                "state": name,
                "subset": natural_sorted(subset),
                "accepting": accepting,
                "moves": moves,
            },
        ))
    dfa = DFA(
        states=frozenset(names.values()),
        alphabet=nfa.alphabet,
        start="d0",
        accepting=frozenset(
            names[subset] for subset in subsets if subset & nfa.accepting
        ),
        transitions=transitions,
        labels={names[subset]: tuple(natural_sorted(subset)) for subset in subsets},
    )
    dfa.validate()
    return dfa, cap_steps(steps)
