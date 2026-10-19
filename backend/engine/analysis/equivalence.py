"""Shortest-counterexample DFA equivalence checking."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from engine.analysis.align import align
from engine.automata.model import DFA
from engine.automata.simulate import simulate
from engine.steps import Step
from engine.util import natural_sorted


@dataclass(frozen=True)
class EquivalenceResult:
    """Equivalence verdict and an optional shortest counterexample."""

    equivalent: bool
    counterexample: str | None
    a_accepts: bool | None
    b_accepts: bool | None
    steps: tuple[Step, ...]


def check_equivalence(a: DFA, b: DFA) -> EquivalenceResult:
    """Find the shortest string on which two DFAs disagree."""
    left, right = align(a, b)
    queue = deque([(left.start, right.start, "")])
    seen = {(left.start, right.start)}
    steps: list[Step] = []
    while queue:
        left_state, right_state, word = queue.popleft()
        left_accepts = left_state in left.accepting
        right_accepts = right_state in right.accepting
        steps.append(Step(
            "Compare states",
            "Compare the two aligned DFA states.",
            {"left": left_state, "right": right_state, "word": word},
        ))
        if left_accepts != right_accepts:
            a_accepts = simulate(a, word).accepted
            b_accepts = simulate(b, word).accepted
            if a_accepts == b_accepts:
                raise RuntimeError("equivalence self-check failed")
            return EquivalenceResult(False, word, a_accepts, b_accepts, tuple(steps))
        for symbol in natural_sorted(left.alphabet):
            target = (left.transitions[(left_state, symbol)], right.transitions[(right_state, symbol)])
            if target not in seen:
                seen.add(target)
                queue.append((*target, word + symbol))
    return EquivalenceResult(True, None, None, None, tuple(steps))
