"""NFA and DFA simulation with human-readable explanations."""

from __future__ import annotations

from dataclasses import dataclass

from engine.automata.model import DFA, EPSILON, NFA
from engine.util import natural_sorted


@dataclass(frozen=True)
class SimStep:
    """One configuration before and after reading a symbol."""

    index: int
    symbol: str | None
    before: tuple[str, ...]
    after: tuple[str, ...]
    via_epsilon: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class SimulationResult:
    """The result and explanation of a simulation."""

    accepted: bool
    steps: tuple[SimStep, ...]
    reason: str
    rejected_at: int | None


def simulate(automaton: NFA | DFA, string: str) -> SimulationResult:
    """Simulate a string on an NFA or partial DFA."""
    automaton.validate()
    if any(ch not in automaton.alphabet for ch in string):
        missing = next(ch for ch in string if ch not in automaton.alphabet)
        alphabet = ", ".join(natural_sorted(automaton.alphabet))
        return SimulationResult(
            False, (), f"Rejected: symbol '{missing}' is not in the alphabet {{{alphabet}}}.", 0
        )
    if isinstance(automaton, DFA):
        return _simulate_dfa(automaton, string)
    return _simulate_nfa(automaton, string)


def _simulate_dfa(automaton: DFA, string: str) -> SimulationResult:
    current = automaton.start
    steps = [SimStep(0, None, (current,), (current,), (), "Start at the DFA start state.")]
    for index, symbol in enumerate(string, 1):
        target = automaton.transitions.get((current, symbol))
        if target is None:
            reason = f"Rejected: no transition from {current} on '{symbol}'."
            return SimulationResult(False, tuple(steps), reason, index)
        steps.append(SimStep(
            index, symbol, (current,), (target,), (),
            f"Follow the transition from {current} on '{symbol}' to {target}.",
        ))
        current = target
    if current in automaton.accepting:
        return SimulationResult(
            True, tuple(steps), f"Accepted: ended in accepting state {current}.", None
        )
    return SimulationResult(
        False,
        tuple(steps),
        f"Rejected: ended in {{{current}}}, none of which is accepting.",
        len(steps) - 1,
    )


def _simulate_nfa(automaton: NFA, string: str) -> SimulationResult:
    current = _epsilon_closure(automaton, {automaton.start})
    initial_added = tuple(state for state in natural_sorted(current) if state != automaton.start)
    steps = [SimStep(
        0, None, (automaton.start,), tuple(natural_sorted(current)), initial_added,
        "Start at the ε-closure of the NFA start state.",
    )]
    for index, symbol in enumerate(string, 1):
        before = current
        moved = {
            target
            for source in current
            for target in automaton.transitions.get((source, symbol), frozenset())
        }
        current = _epsilon_closure(automaton, moved)
        via_epsilon = tuple(state for state in natural_sorted(current) if state not in moved)
        steps.append(SimStep(
            index, symbol, tuple(natural_sorted(before)), tuple(natural_sorted(current)),
            via_epsilon, f"Read '{symbol}' from all active NFA states and take ε-closure.",
        ))
        if not current:
            active = ", ".join(natural_sorted(before))
            return SimulationResult(
                False, tuple(steps),
                f"Rejected: no state in {{{active}}} can read '{symbol}'.", index,
            )
    accepting = automaton.accepting & current
    if accepting:
        state = natural_sorted(accepting)[0]
        return SimulationResult(
            True, tuple(steps), f"Accepted: ended in accepting state {state}.", None
        )
    ended = ", ".join(natural_sorted(current))
    return SimulationResult(
        False, tuple(steps),
        f"Rejected: ended in {{{ended}}}, none of which is accepting.",
        len(steps) - 1,
    )


def _epsilon_closure(automaton: NFA, states: set[str]) -> frozenset[str]:
    closure = set(states)
    pending = list(states)
    while pending:
        state = pending.pop()
        for target in automaton.transitions.get((state, EPSILON), frozenset()):
            if target not in closure:
                closure.add(target)
                pending.append(target)
    return frozenset(closure)
