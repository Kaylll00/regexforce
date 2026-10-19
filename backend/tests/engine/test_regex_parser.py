import pytest
from hypothesis import given, settings

from engine.errors import RegexSyntaxError, UnsupportedFeatureError
from engine.regex.ast import Concat, Epsilon, Star, Symbol, Union
from engine.regex.parser import parse
from engine.regex.printer import to_string
from tests.engine.strategies import regex_asts


def test_precedence_and_left_associativity() -> None:
    node, _ = parse("ab|c*")
    assert node == Union(Concat(Symbol("a"), Symbol("b")), Star(Symbol("c")))


def test_escapes_and_special_values() -> None:
    node, _ = parse(r"\|\*\(\)\\ \e\0")
    assert isinstance(node, Concat)
    assert node == Concat(
        Concat(
            Concat(
                Concat(Concat(Concat(Symbol("|"), Symbol("*")), Symbol("(")), Symbol(")")),
                Symbol("\\"),
            ),
            Epsilon(),
        ),
        parse(r"\0")[0],
    )

    epsilon_empty, _ = parse("ε∅")
    assert epsilon_empty == Concat(Epsilon(), parse(r"\0")[0])


def test_sugar_and_textbook_union() -> None:
    plus, plus_steps = parse("a+")
    optional, optional_steps = parse("a?")
    textbook, textbook_steps = parse("a+b", textbook=True)
    assert plus == Concat(Symbol("a"), Star(Symbol("a")))
    assert optional == Union(Symbol("a"), Epsilon())
    assert textbook == Union(Symbol("a"), Symbol("b"))
    assert len(plus_steps) == len(optional_steps) == 1
    assert textbook_steps == []


@pytest.mark.parametrize(
    ("expression", "position"),
    [("|a", 0), ("a|", 1), ("()", 0), ("*a", 0), ("a)", 1), ("(a", 0), ("\\", 0)],
)
def test_syntax_errors_have_positions(expression: str, position: int) -> None:
    with pytest.raises(RegexSyntaxError) as error:
        parse(expression)
    assert error.value.position == position


@pytest.mark.parametrize(
    "expression",
    [".", "[a]", "a{2}", "^a", "a$", r"\1", "(?:a)", "a*?", "a+?", "a++", "a??"],
)
def test_unsupported_features_are_rejected(expression: str) -> None:
    with pytest.raises(UnsupportedFeatureError):
        parse(expression)


@settings(max_examples=100)
@given(regex_asts())
def test_printer_round_trip(node) -> None:
    assert parse(to_string(node))[0] == node
