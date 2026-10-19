"""GNFA state-elimination conversion from automata to regexes."""

from __future__ import annotations

from collections import defaultdict, deque

from engine.automata.model import DFA, EPSILON, NFA
from engine.automata.nfa_ops import dfa_to_nfa
from engine.conversion.simplify import simplify
from engine.regex.ast import Concat, Empty, Epsilon, Node, Star, Symbol, Union
from engine.regex.printer import to_string
from engine.steps import Step
from engine.util import cap_steps, natural_sorted


def automaton_to_regex_state_elimination(a: NFA | DFA) -> tuple[Node, list[Step]]:
    """Convert an automaton to a regex by eliminating GNFA states."""
    nfa = dfa_to_nfa(a) if isinstance(a, DFA) else a
    useful = _useful_states(nfa)
    steps: list[Step] = [Step(
        "Prune automaton",
        "Remove states that are unreachable or cannot reach an accepting state.",
        {"removed": natural_sorted(nfa.states - useful)},
    )]
    if nfa.start not in useful:
        return Empty(), steps + [Step("Finish conversion", "No accepting path remains.", {"regex": "∅"})]
    start, finish = _fresh("S", useful), _fresh("F", useful)
    active = set(useful) | {start, finish}
    edges: dict[tuple[str, str], Node] = {}

    def add(source: str, target: str, label: Node) -> None:
        key = (source, target)
        edges[key] = simplify(Union(edges[key], label)) if key in edges else label

    add(start, nfa.start, Epsilon())
    for accepting in nfa.accepting & useful:
        add(accepting, finish, Epsilon())
    for (source, symbol), targets in nfa.transitions.items():
        if source not in useful:
            continue
        for target in targets:
            if target in useful:
                add(source, target, Epsilon() if symbol == EPSILON else Symbol(symbol))

    while active - {start, finish}:
        candidates = []
        for state in active - {start, finish}:
            incoming = sum(1 for source, target in edges if target == state and source != state)
            outgoing = sum(1 for source, target in edges if source == state and target != state)
            candidates.append((incoming * outgoing, str(state), state))
        _, _, removed = min(candidates, key=lambda item: (item[0], natural_sorted([item[1]])[0]))
        predecessors = natural_sorted({source for source, target in edges if target == removed and source != removed})
        successors = natural_sorted({target for source, target in edges if source == removed and target != removed})
        loop = Star(edges[(removed, removed)]) if (removed, removed) in edges else Epsilon()
        updates = []
        for source in predecessors:
            for target in successors:
                candidate = _concat(edges[(source, removed)], loop, edges[(removed, target)])
                key = (source, target)
                result = simplify(Union(edges[key], candidate)) if key in edges else simplify(candidate)
                edges[key] = result
                updates.append({
                    "from": source, "to": target,
                    "formula": f"{to_string(edges[(source, removed)])}{to_string(loop)}{to_string(edges[(removed, target)])}",
                    "result": to_string(result),
                })
        edges = {
            key: value for key, value in edges.items()
            if removed not in key
        }
        active.remove(removed)
        steps.append(Step(
            f"Eliminate state {removed}",
            "Redirect paths through the removed state using its loop expression.",
            {"removed": removed, "updates": updates},
        ))
    result = simplify(edges.get((start, finish), Empty()))
    steps.append(Step("Finish conversion", "The remaining start-to-accept expression is the result.",
                       {"regex": to_string(result)}))
    return result, cap_steps(steps)


def _concat(*nodes: Node) -> Node:
    result = nodes[0]
    for node in nodes[1:]:
        if isinstance(result, Empty) or isinstance(node, Empty):
            return Empty()
        if isinstance(result, Epsilon):
            result = node
        elif isinstance(node, Epsilon):
            continue
        else:
            result = Concat(result, node)
    return result


def _useful_states(nfa: NFA) -> set[str]:
    reachable = {nfa.start}
    queue = deque([nfa.start])
    while queue:
        source = queue.popleft()
        for target in nfa.transitions.get((source, EPSILON), frozenset()) | frozenset(
            target for (state, _), targets in nfa.transitions.items() if state == source for target in targets
        ):
            if target not in reachable:
                reachable.add(target)
                queue.append(target)
    reverse: dict[str, set[str]] = defaultdict(set)
    for (source, _), targets in nfa.transitions.items():
        for target in targets:
            reverse[target].add(source)
    co_reachable = set(nfa.accepting)
    queue = deque(nfa.accepting)
    while queue:
        target = queue.popleft()
        for source in reverse[target]:
            if source not in co_reachable:
                co_reachable.add(source)
                queue.append(source)
    return reachable & co_reachable


def _fresh(base: str, states: set[str]) -> str:
    value = base
    index = 1
    while value in states:
        value = f"{base}{index}"
        index += 1
    return value
