"""The standard regex-to-automata build pipeline."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from engine.automata.dfa_ops import complete_dfa, minimize_dfa
from engine.automata.model import DFA, NFA
from engine.automata.subset import nfa_to_dfa
from engine.automata.thompson import regex_to_nfa
from engine.regex.ast import Node
from engine.regex.printer import to_string
from engine.steps import Step


@dataclass(frozen=True)
class PipelineResult:
    """All stages and explanations produced from one regex AST."""

    nfa: NFA
    dfa: DFA
    min_dfa: DFA
    steps_by_stage: dict[str, list[Step]]


def build_pipeline(node: Node, alphabet: Iterable[str] | None = None) -> PipelineResult:
    """Build Thompson, completed subset, and minimized DFA stages."""
    nfa, nfa_steps = regex_to_nfa(node, alphabet)
    partial, subset_steps = nfa_to_dfa(nfa)
    dfa, complete_steps = complete_dfa(partial, alphabet)
    min_dfa, minimum_steps = minimize_dfa(dfa)
    return PipelineResult(
        nfa=nfa,
        dfa=dfa,
        min_dfa=min_dfa,
        steps_by_stage={
            "parse": [Step("Parse regex", f"Use the parsed expression {to_string(node)}.", {})],
            "nfa": nfa_steps,
            "dfa": [*subset_steps, *complete_steps],
            "min_dfa": minimum_steps,
        },
    )
