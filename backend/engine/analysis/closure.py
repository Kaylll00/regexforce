"""Regular-language closure operations."""

from __future__ import annotations

from engine.analysis.align import align
from engine.analysis.product import product
from engine.automata.dfa_ops import complete_dfa, minimize_dfa
from engine.automata.model import DFA, EPSILON, NFA
from engine.automata.nfa_ops import dfa_to_nfa, reverse_nfa
from engine.automata.subset import nfa_to_dfa
from engine.errors import EngineError
from engine.steps import Step


def apply_closure(op: str, operands: list[DFA], minimize: bool = True) -> tuple[DFA, list[Step]]:
    """Apply a named regular-language closure operation."""
    if op in {"union", "intersection", "difference", "symmetric_difference"}:
        if len(operands) != 2:
            raise EngineError("Binary closure operations require two operands.")
        left, right = align(operands[0], operands[1])
        predicates = {
            "union": lambda a, b: a or b,
            "intersection": lambda a, b: a and b,
            "difference": lambda a, b: a and not b,
            "symmetric_difference": lambda a, b: a != b,
        }
        result, steps = product(left, right, predicates[op])
    elif op == "complement":
        if len(operands) != 1:
            raise EngineError("Complement requires one operand.")
        result, completion_steps = complete_dfa(operands[0])
        result = DFA(result.states, result.alphabet, result.start, result.states - result.accepting,
                     result.transitions, result.labels)
        steps = [*completion_steps, Step("Complement", "Flip accepting and non-accepting states.", {})]
    elif op in {"concatenation", "star", "reversal"}:
        nfa, steps = _build_nfa(op, operands)
        result, subset_steps = nfa_to_dfa(nfa)
        steps.extend(subset_steps)
    else:
        raise EngineError(f"Unknown closure operation: {op}.")
    if minimize:
        result, minimum_steps = minimize_dfa(result)
        steps.extend(minimum_steps)
    return result, steps


def _build_nfa(op: str, operands: list[DFA]) -> tuple[NFA, list[Step]]:
    if op == "reversal":
        if len(operands) != 1:
            raise EngineError("Reversal requires one operand.")
        return reverse_nfa(dfa_to_nfa(operands[0])), []
    if op == "star":
        if len(operands) != 1:
            raise EngineError("Star requires one operand.")
        base = dfa_to_nfa(operands[0])
        start, finish = "closure_start", "closure_accept"
        transitions = dict(base.transitions)
        transitions[(start, EPSILON)] = frozenset({base.start, finish})
        for state in base.accepting:
            transitions[(state, EPSILON)] = frozenset(
                set(transitions.get((state, EPSILON), frozenset())) | {base.start, finish}
            )
        return NFA(base.states | {start, finish}, base.alphabet, start, frozenset({finish}), transitions), []
    if len(operands) != 2:
        raise EngineError("Concatenation requires two operands.")
    left, right = dfa_to_nfa(operands[0]), dfa_to_nfa(operands[1])
    left_states = {f"l_{state}" for state in left.states}
    right_states = {f"r_{state}" for state in right.states}
    concat_transitions: dict[tuple[str, str], frozenset[str]] = {}
    for (source, symbol), targets in left.transitions.items():
        concat_transitions[(f"l_{source}", symbol)] = frozenset(
            f"l_{target}" for target in targets
        )
    for (source, symbol), targets in right.transitions.items():
        concat_transitions[(f"r_{source}", symbol)] = frozenset(
            f"r_{target}" for target in targets
        )
    for state in left.accepting:
        key = (f"l_{state}", EPSILON)
        concat_transitions[key] = frozenset(
            set(concat_transitions.get(key, frozenset())) | {f"r_{right.start}"}
        )
    return NFA(
        frozenset(left_states | right_states), left.alphabet | right.alphabet,
        f"l_{left.start}", frozenset(f"r_{state}" for state in right.accepting), concat_transitions,
    ), []
