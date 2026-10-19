from engine.analysis.closure import apply_closure
from engine.analysis.equivalence import check_equivalence
from engine.analysis.properties import (
    compare,
    is_empty,
    is_finite,
    is_subset,
    is_universal,
    overlap,
    shortest_accepted,
)
from engine.analysis.rules import resolve_rule
from engine.analysis.rules_set import compare_many
from engine.automata.simulate import simulate
from tests.engine.helpers import all_strings


def rule(expression: str):
    return resolve_rule({"kind": "regex", "regex": expression})[0]


def test_equivalence_finds_shortest_counterexample() -> None:
    result = check_equivalence(rule("(a|b)*abb"), rule("(a|b)*ab"))
    assert not result.equivalent
    assert result.counterexample == "ab"
    assert result.a_accepts is False
    assert result.b_accepts is True


def test_known_equivalent_rules() -> None:
    assert check_equivalence(rule("(a|b)*"), rule("(a*b*)*")).equivalent
    assert check_equivalence(rule("a(ba)*"), rule("(ab)*a")).equivalent


def test_closure_operations_against_expected_languages() -> None:
    a, b = rule("a"), rule("b")
    operations = {
        "union": {"a", "b"},
        "intersection": set(),
        "difference": {"a"},
        "symmetric_difference": {"a", "b"},
    }
    for operation, expected in operations.items():
        result, _ = apply_closure(operation, [a, b])
        assert {
            value for value in all_strings("ab", 2) if simulate(result, value).accepted
        } == expected
    star, _ = apply_closure("star", [a])
    assert simulate(star, "aaa").accepted
    assert not simulate(star, "ab").accepted


def test_properties_and_witnesses() -> None:
    empty = rule("∅")
    epsilon = rule("ε")
    universal = rule("(a|b)*")
    assert is_empty(empty)
    assert shortest_accepted(empty) is None
    assert shortest_accepted(epsilon) == ""
    assert is_finite(rule("a|b"))
    assert not is_finite(rule("a*"))
    assert is_universal(universal)
    assert is_subset(rule("a"), rule("a|b")) == (True, None)
    assert overlap(rule("a|b"), rule("b|ε")) == "b"
    assert compare(rule("a"), rule("a|b")).relation == "a_subset_b"


def test_resolve_rule_and_compare_many() -> None:
    dfa = rule("a")
    grammar_dfa, _ = resolve_rule({"kind": "grammar", "grammar": "S -> a"})
    assert check_equivalence(dfa, grammar_dfa).equivalent
    report = compare_many([("small", dfa), ("large", rule("a|b")), ("duplicate", dfa)])
    assert report.redundant == ["small", "duplicate"]
