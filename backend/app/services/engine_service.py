"""Thin JSON adapters around the formal-language engine."""

from __future__ import annotations

from engine.automata.model import DFA, NFA, transition_table
from engine.conversion.pipeline import build_pipeline
from engine.regex.ast import alphabet_of, to_dict
from engine.regex.parser import parse
from engine.regex.printer import to_string


def parse_regex(regex: str, textbook: bool = False) -> dict:
    node, steps = parse(regex, textbook=textbook)
    from engine.regex.highlight import highlight_tokens
    return {
        "canonical": to_string(node),
        "ast": to_dict(node),
        "alphabet": sorted(alphabet_of(node)),
        "tokens": [token.__dict__ for token in highlight_tokens(regex, textbook=textbook)],
        "steps": [step.to_dict() for step in steps],
    }


def build_regex(regex: str, textbook: bool = False, alphabet: list[str] | None = None) -> dict:
    node, _ = parse(regex, textbook=textbook)
    pipeline = build_pipeline(node, alphabet)
    return {
        "canonical": to_string(node),
        "alphabet": sorted(pipeline.dfa.alphabet),
        "nfa": pipeline.nfa.to_dict(),
        "dfa": pipeline.dfa.to_dict(),
        "min_dfa": pipeline.min_dfa.to_dict(),
        "tables": {
            "nfa": transition_table(pipeline.nfa),
            "dfa": transition_table(pipeline.dfa),
            "min_dfa": transition_table(pipeline.min_dfa),
        },
        "steps_by_stage": {
            key: [step.to_dict() for step in value]
            for key, value in pipeline.steps_by_stage.items()
        },
    }


def get_automaton(data: dict) -> NFA | DFA:
    return NFA.from_dict(data) if data.get("type") == "nfa" else DFA.from_dict(data)


def automaton_result(automaton: NFA | DFA) -> dict:
    return {"automaton": automaton.to_dict(), "table": transition_table(automaton)}


def steps_result(automaton: NFA | DFA, steps) -> dict:
    return {
        "automaton": automaton.to_dict(),
        "table": transition_table(automaton),
        "steps": [step.to_dict() for step in steps],
    }
