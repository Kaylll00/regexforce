import pytest

from engine.automata.model import DFA
from engine.automata.thompson import regex_to_nfa
from engine.conversion.arden import automaton_to_regex_arden
from engine.conversion.pipeline import build_pipeline
from engine.conversion.simplify import simplify
from engine.conversion.state_elimination import automaton_to_regex_state_elimination
from engine.regex.ast import Concat, Empty, Epsilon, Star, Symbol, Union
from engine.regex.derivative import matches
from engine.regex.parser import parse
from tests.engine.helpers import all_strings


@pytest.mark.parametrize("expression", ["a", "ab", "a|b", "a*", "(a|b)*abb"])
def test_both_conversions_preserve_language(expression: str) -> None:
    node, _ = parse(expression)
    nfa, _ = regex_to_nfa(node)
    state_regex, state_steps = automaton_to_regex_state_elimination(nfa)
    arden_regex, arden_steps = automaton_to_regex_arden(nfa)
    assert state_steps
    assert arden_steps
    for value in all_strings("ab", 4):
        assert matches(state_regex, value) == matches(node, value)
        assert matches(arden_regex, value) == matches(node, value)


def test_simplification_rules() -> None:
    a = Symbol("a")
    assert simplify(Union(Empty(), a)) == a
    assert simplify(Union(a, a)) == a
    assert simplify(Concat(Empty(), a)) == Empty()
    assert simplify(Concat(Epsilon(), a)) == a
    assert simplify(Star(Empty())) == Epsilon()
    assert simplify(Star(Star(a))) == Star(a)


def test_pipeline_has_required_stages_and_four_state_minimum() -> None:
    node, _ = parse("(a|b)*abb")
    result = build_pipeline(node)
    assert set(result.steps_by_stage) == {"parse", "nfa", "dfa", "min_dfa"}
    assert len(result.min_dfa.states) == 4


def test_empty_and_epsilon_automata() -> None:
    empty = DFA(frozenset({"q0"}), frozenset({"a"}), "q0", frozenset(), {})
    epsilon = DFA(frozenset({"q0"}), frozenset({"a"}), "q0", frozenset({"q0"}), {})
    empty_regex, _ = automaton_to_regex_state_elimination(empty)
    epsilon_regex, _ = automaton_to_regex_arden(epsilon)
    assert empty_regex == Empty()
    assert matches(epsilon_regex, "")
    assert not matches(epsilon_regex, "a")
