import pytest

from engine.automata.dfa_ops import complete_dfa, minimize_dfa
from engine.automata.model import DFA, EPSILON, NFA, transition_table
from engine.automata.nfa_ops import reverse_nfa
from engine.automata.simulate import simulate
from engine.automata.subset import nfa_to_dfa
from engine.automata.thompson import regex_to_nfa
from engine.errors import AutomatonError
from engine.regex.derivative import matches
from engine.regex.parser import parse
from tests.engine.helpers import all_strings


def build(expression: str):
    node, _ = parse(expression)
    nfa, _ = regex_to_nfa(node)
    dfa, _ = nfa_to_dfa(nfa)
    return node, nfa, dfa


@pytest.mark.parametrize("expression", ["a", "ab", "a|b", "a*", "(a|b)*abb"])
def test_pipeline_preserves_reference_language(expression: str) -> None:
    node, nfa, dfa = build(expression)
    complete, _ = complete_dfa(dfa)
    minimum, _ = minimize_dfa(dfa)
    for value in all_strings("ab", 5):
        assert simulate(nfa, value).accepted == matches(node, value)
        assert simulate(dfa, value).accepted == matches(node, value)
        assert simulate(complete, value).accepted == matches(node, value)
        assert simulate(minimum, value).accepted == matches(node, value)


def test_known_minimum_has_four_states() -> None:
    _, _, dfa = build("(a|b)*abb")
    minimum, _ = minimize_dfa(dfa)
    assert len(minimum.states) == 4


def test_simulation_reason_formats() -> None:
    _, nfa, dfa = build("a")
    assert simulate(dfa, "b").reason == "Rejected: symbol 'b' is not in the alphabet {a}."
    partial, _ = nfa_to_dfa(nfa)
    assert simulate(partial, "").reason.startswith("Rejected: ended")
    assert simulate(dfa, "a").reason == "Accepted: ended in accepting state d1."


def test_transition_table_has_epsilon_column() -> None:
    _, nfa, _ = build("a")
    table = transition_table(nfa)
    assert table["has_epsilon"] is False
    epsilon_nfa = NFA(
        frozenset({"q0", "q1"}), frozenset({"a"}), "q0", frozenset({"q1"}),
        {("q0", EPSILON): frozenset({"q1"})},
    )
    assert transition_table(epsilon_nfa)["has_epsilon"] is True
    assert "ε" in transition_table(epsilon_nfa)["rows"][0]["cells"]


def test_automaton_round_trip_and_validation() -> None:
    _, nfa, _ = build("a")
    assert NFA.from_dict(nfa.to_dict()) == nfa
    with pytest.raises(AutomatonError):
        DFA.from_dict({
            "type": "dfa",
            "alphabet": ["a"],
            "states": ["q0", "q1"],
            "start": "q0",
            "accepting": [],
            "transitions": [
                {"from": "q0", "symbol": "a", "to": "q0"},
                {"from": "q0", "symbol": "a", "to": "q1"},
            ],
        })


def test_reverse_accepts_reversed_words() -> None:
    _, nfa, _ = build("ab")
    reversed_nfa = reverse_nfa(nfa)
    for value in all_strings("ab", 3):
        assert simulate(reversed_nfa, value).accepted == simulate(nfa, value[::-1]).accepted
