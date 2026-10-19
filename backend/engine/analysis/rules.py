"""Resolve user rules into complete minimized DFAs."""

from __future__ import annotations

from collections.abc import Iterable

from engine.automata.dfa_ops import complete_dfa, minimize_dfa
from engine.automata.model import DFA, NFA
from engine.automata.subset import nfa_to_dfa
from engine.automata.thompson import regex_to_nfa
from engine.grammar.convert import grammar_to_nfa
from engine.grammar.parser import parse_grammar
from engine.regex.parser import parse
from engine.steps import Step


def resolve_rule(rule: dict, alphabet: Iterable[str] | None = None) -> tuple[DFA, list[Step]]:
    """Resolve a regex, automaton, or grammar rule to a complete minimized DFA."""
    kind = rule.get("kind")
    steps: list[Step] = []
    if kind == "regex":
        node, parse_steps = parse(rule["regex"], textbook=bool(rule.get("textbook", False)))
        nfa, nfa_steps = regex_to_nfa(node, alphabet)
        steps.extend([*parse_steps, *nfa_steps])
    elif kind == "automaton":
        automaton = NFA.from_dict(rule["automaton"]) if rule["automaton"].get("type") == "nfa" else DFA.from_dict(rule["automaton"])
        if isinstance(automaton, DFA):
            dfa = automaton
            if alphabet:
                dfa, complete_steps = complete_dfa(dfa, alphabet)
                steps.extend(complete_steps)
            minimum, minimum_steps = minimize_dfa(dfa)
            return minimum, steps + minimum_steps
        nfa = automaton
    elif kind == "grammar":
        grammar, grammar_steps = parse_grammar(rule["grammar"])
        nfa, nfa_steps = grammar_to_nfa(grammar)
        steps.extend([*grammar_steps, *nfa_steps])
    else:
        raise ValueError("Rule kind must be regex, automaton, or grammar.")
    dfa, subset_steps = nfa_to_dfa(nfa)
    complete, complete_steps = complete_dfa(dfa, alphabet)
    minimum, minimum_steps = minimize_dfa(complete)
    return minimum, steps + subset_steps + complete_steps + minimum_steps
