"""Thompson construction from regex ASTs to NFAs."""

from __future__ import annotations

from collections.abc import Iterable

from engine.automata.model import EPSILON, NFA
from engine.regex.ast import Concat, Empty, Epsilon, Node, Symbol, Union, alphabet_of
from engine.regex.printer import to_string
from engine.steps import Step
from engine.util import cap_steps, natural_sorted


def regex_to_nfa(node: Node, alphabet: Iterable[str] | None = None) -> tuple[NFA, list[Step]]:
    """Build a Thompson NFA with one fragment per AST node."""
    transitions: dict[tuple[str, str], set[str]] = {}
    states: list[str] = []
    counter = 0
    steps: list[Step] = []

    def state() -> str:
        nonlocal counter
        value = f"q{counter}"
        counter += 1
        states.append(value)
        return value

    def edge(source: str, symbol: str, target: str) -> None:
        transitions.setdefault((source, symbol), set()).add(target)

    def build(current: Node) -> tuple[str, str]:
        if isinstance(current, Symbol):
            start, accept = state(), state()
            edge(start, current.char, accept)
        elif isinstance(current, Epsilon):
            start, accept = state(), state()
            edge(start, EPSILON, accept)
        elif isinstance(current, Empty):
            start, accept = state(), state()
        elif isinstance(current, Concat):
            left_start, left_accept = build(current.left)
            right_start, right_accept = build(current.right)
            edge(left_accept, EPSILON, right_start)
            start, accept = left_start, right_accept
        elif isinstance(current, Union):
            left_start, left_accept = build(current.left)
            right_start, right_accept = build(current.right)
            start, accept = state(), state()
            edge(start, EPSILON, left_start)
            edge(start, EPSILON, right_start)
            edge(left_accept, EPSILON, accept)
            edge(right_accept, EPSILON, accept)
        else:
            inner_start, inner_accept = build(current.inner)
            start, accept = state(), state()
            edge(start, EPSILON, inner_start)
            edge(start, EPSILON, accept)
            edge(inner_accept, EPSILON, inner_start)
            edge(inner_accept, EPSILON, accept)
        steps.append(Step(
            "Build fragment",
            f"Built a Thompson fragment for {to_string(current)}.",
            {"node": to_string(current), "start": start, "accept": accept},
        ))
        return start, accept

    start, accept = build(node)
    symbols = alphabet_of(node) | frozenset(alphabet or ())
    nfa = NFA(
        states=frozenset(states),
        alphabet=frozenset(symbols),
        start=start,
        accepting=frozenset({accept}),
        transitions={key: frozenset(natural_sorted(value)) for key, value in transitions.items()},
    )
    nfa.validate()
    return nfa, cap_steps(steps)
