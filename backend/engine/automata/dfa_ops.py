"""Completion and Moore minimization for deterministic automata."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from engine.automata.model import DFA
from engine.errors import LimitError
from engine.steps import Step
from engine.util import cap_steps, natural_sorted


def remove_unreachable(dfa: DFA) -> tuple[DFA, list[Step]]:
    """Remove states that cannot be reached from the DFA start."""
    reachable = {dfa.start}
    queue = deque([dfa.start])
    while queue:
        state = queue.popleft()
        for symbol in natural_sorted(dfa.alphabet):
            target = dfa.transitions.get((state, symbol))
            if target is not None and target not in reachable:
                reachable.add(target)
                queue.append(target)
    result = DFA(
        frozenset(reachable),
        dfa.alphabet,
        dfa.start,
        dfa.accepting & reachable,
        {key: target for key, target in dfa.transitions.items() if key[0] in reachable and target in reachable},
        {key: value for key, value in dfa.labels.items() if key in reachable},
    )
    result.validate()
    return result, cap_steps([Step(
        "Remove unreachable states",
        "Keep only states reachable from the start state.",
        {"removed": natural_sorted(dfa.states - reachable)},
    )])


def complete_dfa(dfa: DFA, alphabet: Iterable[str] | None = None) -> tuple[DFA, list[Step]]:
    """Add a sink state and missing transitions so every input has a move."""
    symbols = frozenset(dfa.alphabet | frozenset(alphabet or ()))
    missing = [
        (state, symbol)
        for state in dfa.states
        for symbol in symbols
        if (state, symbol) not in dfa.transitions
    ]
    if not missing:
        if symbols == dfa.alphabet:
            return dfa, []
        expanded = DFA(dfa.states, symbols, dfa.start, dfa.accepting, dfa.transitions, dfa.labels)
        expanded.validate()
        return expanded, []
    dead = "dead"
    while dead in dfa.states:
        dead += "1"
    transitions = dict(dfa.transitions)
    for state, symbol in missing:
        transitions[(state, symbol)] = dead
    for symbol in symbols:
        transitions[(dead, symbol)] = dead
    result = DFA(
        dfa.states | {dead}, symbols, dfa.start, dfa.accepting, transitions,
        {**dfa.labels, dead: ("dead",)},
    )
    result.validate()
    return result, cap_steps([Step(
        "Complete DFA",
        f"Add sink state {dead} for every missing transition.",
        {"dead_state": dead, "alphabet": natural_sorted(symbols)},
    )])


def minimize_dfa(dfa: DFA, trim_dead: bool = False) -> tuple[DFA, list[Step]]:
    """Minimize a complete DFA; trim_dead removes the display-only sink afterward."""
    reachable, initial_steps = remove_unreachable(dfa)
    complete, completion_steps = complete_dfa(reachable)
    accepting = frozenset(complete.accepting)
    partitions: list[frozenset[str]] = [
        group for group in (
            frozenset(complete.states - accepting),
            accepting,
        ) if group
    ]
    steps = [*initial_steps, *completion_steps]
    while True:
        groups = {state: index for index, group in enumerate(partitions) for state in group}
        refined: list[frozenset[str]] = []
        for group in partitions:
            buckets: dict[tuple[int, ...], set[str]] = {}
            for state in natural_sorted(group):
                signature = tuple(
                    groups[complete.transitions[(state, symbol)]]
                    for symbol in natural_sorted(complete.alphabet)
                )
                buckets.setdefault(signature, set()).add(state)
            refined.extend(frozenset(bucket) for bucket in buckets.values())
        steps.append(Step(
            "Refine partition",
            "Split states with different transition signatures.",
            {"round": len(steps), "partition": [natural_sorted(group) for group in refined]},
        ))
        if refined == partitions:
            break
        partitions = refined
        if len(partitions) > 2000:
            raise LimitError("DFA minimization exceeded 2000 states.")
    block_for = {state: index for index, group in enumerate(partitions) for state in group}
    block_names: dict[int, str] = {}
    queue = deque([block_for[complete.start]])
    while queue:
        block = queue.popleft()
        if block in block_names:
            continue
        block_names[block] = f"m{len(block_names)}"
        representative = next(iter(partitions[block]))
        for symbol in natural_sorted(complete.alphabet):
            target_block = block_for[complete.transitions[(representative, symbol)]]
            if target_block not in block_names:
                queue.append(target_block)
    transitions = {}
    labels = {}
    accepting_states = set()
    for block, name in block_names.items():
        members = partitions[block]
        labels[name] = tuple(natural_sorted(members))
        if members & complete.accepting:
            accepting_states.add(name)
        representative = next(iter(members))
        for symbol in natural_sorted(complete.alphabet):
            target_block = block_for[complete.transitions[(representative, symbol)]]
            transitions[(name, symbol)] = block_names[target_block]
    result = DFA(
        frozenset(block_names.values()), complete.alphabet, block_names[block_for[complete.start]],
        frozenset(accepting_states), transitions, labels,
    )
    if trim_dead:
        dead_blocks = [name for name, members in labels.items() if set(members) <= {"dead"}]
        if dead_blocks:
            dead_name = dead_blocks[0]
            result = DFA(
                result.states - {dead_name},
                result.alphabet,
                result.start,
                result.accepting - {dead_name},
                {key: target for key, target in result.transitions.items()
                 if key[0] != dead_name and target != dead_name},
                {key: value for key, value in result.labels.items() if key != dead_name},
            )
    result.validate()
    return result, cap_steps(steps)
