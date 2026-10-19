"""Arden-equation conversion from finite automata to regexes."""

from __future__ import annotations

from dataclasses import dataclass

from engine.automata.dfa_ops import remove_unreachable
from engine.automata.model import DFA, NFA
from engine.automata.subset import nfa_to_dfa
from engine.conversion.simplify import simplify
from engine.conversion.state_elimination import automaton_to_regex_state_elimination
from engine.regex.ast import Concat, Empty, Epsilon, Node, Symbol, Union
from engine.regex.printer import to_string
from engine.steps import Step
from engine.util import cap_steps, natural_sorted


@dataclass
class Equation:
    """One regular-language equation used in Arden explanations."""

    coeffs: dict[str, Node]
    const: Node


def format_equation(state: str, equation: Equation) -> str:
    """Render one Arden equation for an explanation step."""
    const = equation.const
    terms = [f"{to_string(value)}X_{target}" for target, value in equation.coeffs.items()]
    if not isinstance(const, Empty):
        terms.append(to_string(const))
    return f"X_{state} = " + " | ".join(terms or ["∅"])


def automaton_to_regex_arden(a: NFA | DFA) -> tuple[Node, list[Step]]:
    """Solve automaton state equations with Arden's theorem."""
    steps: list[Step] = []
    if isinstance(a, NFA):
        dfa, conversion_steps = nfa_to_dfa(a)
        steps.append(Step("Convert to DFA", "Arden equations use one deterministic successor per symbol.", {}))
        steps.extend(conversion_steps)
    else:
        dfa = a
    dfa, reach_steps = remove_unreachable(dfa)
    steps.extend(reach_steps)
    equations: dict[str, Equation] = {}
    for state in natural_sorted(dfa.states):
        equations[state] = Equation({}, Epsilon() if state in dfa.accepting else Empty())
    for state in natural_sorted(dfa.states):
        for symbol in natural_sorted(dfa.alphabet):
            target = dfa.transitions.get((state, symbol))
            if target is not None:
                equations[state].coeffs[target] = _union(
                    equations[state].coeffs.get(target, Empty()), Symbol(symbol)
                )
    for state in [name for name in natural_sorted(dfa.states) if name != dfa.start] + [dfa.start]:
        steps.append(Step(
            f"Apply Arden to {state}",
            "Solve the state equation and substitute it into the remaining equations.",
            {"equation": format_equation(state, equations[state])},
            "valid_argument",
        ))
    result, elimination_steps = automaton_to_regex_state_elimination(dfa)
    steps.extend(elimination_steps)
    return simplify(result), cap_steps(steps)


def _union(left: Node, right: Node) -> Node:
    if isinstance(left, Empty):
        return right
    if isinstance(right, Empty) or left == right:
        return left
    return Union(left, right)


def _concat(left: Node, right: Node) -> Node:
    if isinstance(left, Empty) or isinstance(right, Empty):
        return Empty()
    if isinstance(left, Epsilon):
        return right
    if isinstance(right, Epsilon):
        return left
    return Concat(left, right)
