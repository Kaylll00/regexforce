"""Language properties and witness relations for complete DFAs."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from engine.analysis.align import align
from engine.automata.dfa_ops import complete_dfa
from engine.automata.model import DFA
from engine.util import natural_sorted


def is_empty(dfa: DFA) -> bool:
    """Return whether no reachable state is accepting."""
    return shortest_accepted(dfa) is None


def is_universal(dfa: DFA) -> bool:
    """Return whether the DFA accepts every string over its alphabet."""
    complete, _ = complete_dfa(dfa)
    complement = DFA(
        complete.states, complete.alphabet, complete.start,
        complete.states - complete.accepting, complete.transitions, complete.labels,
    )
    return is_empty(complement)


def shortest_accepted(dfa: DFA) -> str | None:
    """Return the shortest accepted string, or None for the empty language."""
    queue = deque([(dfa.start, "")])
    seen = {dfa.start}
    while queue:
        state, word = queue.popleft()
        if state in dfa.accepting:
            return word
        for symbol in natural_sorted(dfa.alphabet):
            target = dfa.transitions.get((state, symbol))
            if target is not None and target not in seen:
                seen.add(target)
                queue.append((target, word + symbol))
    return None


def is_finite(dfa: DFA) -> bool:
    """Return whether the accepted language is finite."""
    useful = _useful_states(dfa)
    visiting: set[str] = set()
    visited: set[str] = set()

    def cycle(state: str) -> bool:
        if state in visiting:
            return True
        if state in visited:
            return False
        visiting.add(state)
        for symbol in dfa.alphabet:
            target = dfa.transitions.get((state, symbol))
            if target in useful and cycle(target):
                return True
        visiting.remove(state)
        visited.add(state)
        return False

    return not cycle(dfa.start)


def is_subset(a: DFA, b: DFA) -> tuple[bool, str | None]:
    """Return whether L(a) is a subset of L(b), with a witness if not."""
    left, right = align(a, b)
    found, witness = _witness(left, right, lambda x, y: x and not y)
    return not found, witness


def overlap(a: DFA, b: DFA) -> str | None:
    """Return a shortest string accepted by both DFAs, if one exists."""
    left, right = align(a, b)
    _, witness = _witness(left, right, lambda x, y: x and y)
    return witness


@dataclass(frozen=True)
class RelationResult:
    """Relationship between two languages and witness strings."""

    relation: str
    witnesses: dict[str, str | None]


def compare(a: DFA, b: DFA) -> RelationResult:
    """Classify two languages and return shortest relevant witnesses."""
    ab, a_only = _witness(*align(a, b), lambda x, y: x and not y)
    ba, b_only = _witness(*align(a, b), lambda x, y: y and not x)
    both = overlap(a, b)
    if not ab and not ba:
        return RelationResult("equivalent", {})
    if not ab:
        return RelationResult("a_subset_b", {"witness": b_only})
    if not ba:
        return RelationResult("b_subset_a", {"witness": a_only})
    if both is None:
        return RelationResult("disjoint", {})
    return RelationResult(
        "overlapping",
        {"intersection": both, "a_only": a_only, "b_only": b_only},
    )


def _witness(a: DFA, b: DFA, predicate) -> tuple[bool, str | None]:
    queue = deque([(a.start, b.start, "")])
    seen = {(a.start, b.start)}
    while queue:
        left, right, word = queue.popleft()
        if predicate(left in a.accepting, right in b.accepting):
            return True, word
        for symbol in natural_sorted(a.alphabet):
            target = (a.transitions[(left, symbol)], b.transitions[(right, symbol)])
            if target not in seen:
                seen.add(target)
                queue.append((*target, word + symbol))
    return False, None


def _useful_states(dfa: DFA) -> set[str]:
    reachable = set()
    queue = deque([dfa.start])
    while queue:
        state = queue.popleft()
        if state in reachable:
            continue
        reachable.add(state)
        queue.extend(
            target for symbol in dfa.alphabet
            if (target := dfa.transitions.get((state, symbol))) is not None
        )
    reverse: dict[str, set[str]] = {state: set() for state in dfa.states}
    for (source, _), target in dfa.transitions.items():
        reverse[target].add(source)
    co = set(dfa.accepting)
    queue = deque(co)
    while queue:
        state = queue.popleft()
        for source in reverse[state]:
            if source not in co:
                co.add(source)
                queue.append(source)
    return reachable & co
