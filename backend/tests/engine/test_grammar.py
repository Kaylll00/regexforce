import pytest

from engine.automata.simulate import simulate
from engine.errors import GrammarError
from engine.grammar.convert import (
    grammar_to_nfa,
    grammar_to_regex,
    nfa_to_grammar,
    regex_to_grammar,
)
from engine.grammar.derivation import find_derivation
from engine.grammar.parser import parse_grammar
from engine.grammar.printer import grammar_to_text
from engine.regex.derivative import matches
from engine.regex.parser import parse
from tests.engine.helpers import all_strings


def test_parse_and_print_right_linear_grammar() -> None:
    grammar, steps = parse_grammar("# comment\nS -> aA | b\nA → aS | ε")
    assert grammar.kind == "right-linear"
    assert grammar.start == "S"
    assert steps
    assert "S -> aA | b" in grammar_to_text(grammar)


def test_left_linear_grammar_and_derivation() -> None:
    grammar, _ = parse_grammar("S -> ε | Aa\nA -> a")
    assert grammar.kind == "left-linear"
    derivation, steps = find_derivation(grammar, "aa")
    assert derivation == ["S", "Aa", "aa"]
    assert steps


@pytest.mark.parametrize("text", ["S a", "S -> aB |", "1 -> a", "S -> aBC", "S -> aA | Bb"])
def test_invalid_grammar_has_grammar_error(text: str) -> None:
    with pytest.raises(GrammarError):
        parse_grammar(text)


def test_grammar_nfa_and_derivation_agree() -> None:
    grammar, _ = parse_grammar("S -> aS | bA | ε\nA -> a")
    nfa, _ = grammar_to_nfa(grammar)
    for value in all_strings("ab", 3):
        derivation, _ = find_derivation(grammar, value)
        assert (derivation is not None) == simulate(nfa, value).accepted


def test_grammar_regex_and_automaton_round_trips() -> None:
    node, _ = parse("(a|b)*abb")
    grammar, grammar_steps = regex_to_grammar(node)
    assert grammar_steps
    converted, _ = grammar_to_regex(grammar)
    for value in all_strings("ab", 4):
        assert matches(converted, value) == matches(node, value)
    nfa, _ = grammar_to_nfa(grammar)
    round_trip, _ = nfa_to_grammar(nfa)
    assert round_trip.start == "S"
