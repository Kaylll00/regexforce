"""Operations that transform NFAs without changing their language."""

from __future__ import annotations

from engine.automata.model import DFA, EPSILON, NFA
from engine.steps import Step
from engine.util import cap_steps


def epsilon_closure(nfa: NFA, states: set[str] | frozenset[str]) -> frozenset[str]:
    """Return all states reachable through zero or more ε transitions."""
    closure = set(states)
    pending = list(states)
    while pending:
        state = pending.pop()
        for target in nfa.transitions.get((state, EPSILON), frozenset()):
            if target not in closure:
                closure.add(target)
                pending.append(target)
    return frozenset(closure)


def remove_epsilon(nfa: NFA) -> tuple[NFA, list[Step]]:
    """Remove ε transitions using closure before and after each symbol move."""
    transitions: dict[tuple[str, str], frozenset[str]] = {}
    accepting = set()
    for state in nfa.states:
        closure = epsilon_closure(nfa, {state})
        if closure & nfa.accepting:
            accepting.add(state)
        for symbol in nfa.alphabet:
            targets = {
                target
                for member in closure
                for target in nfa.transitions.get((member, symbol), frozenset())
            }
            if targets:
                transitions[(state, symbol)] = epsilon_closure(nfa, targets)
    result = NFA(nfa.states, nfa.alphabet, nfa.start, frozenset(accepting), transitions, nfa.labels)
    result.validate()
    return result, cap_steps([Step(
        "Remove ε-transitions",
        "Replace each symbol move with closure before and after the move.",
        {"states": len(nfa.states)},
    )])


def reverse_nfa(nfa: NFA) -> NFA:
    """Reverse every edge and exchange the original start and accepting states."""
    new_start = "reverse_start"
    states = set(nfa.states) | {new_start}
    accepting = frozenset({nfa.start})
    transitions: dict[tuple[str, str], set[str]] = {
        (new_start, EPSILON): set(nfa.accepting)
    }
    for (source, symbol), targets in nfa.transitions.items():
        for target in targets:
            transitions.setdefault((target, symbol), set()).add(source)
    result = NFA(
        frozenset(states),
        nfa.alphabet,
        new_start,
        accepting,
        {key: frozenset(value) for key, value in transitions.items()},
    )
    result.validate()
    return result


def dfa_to_nfa(dfa: DFA) -> NFA:
    """View each deterministic transition as a one-target NFA transition."""
    result = NFA(
        dfa.states,
        dfa.alphabet,
        dfa.start,
        dfa.accepting,
        {key: frozenset({target}) for key, target in dfa.transitions.items()},
        dfa.labels,
    )
    result.validate()
    return result
