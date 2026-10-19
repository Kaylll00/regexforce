import pytest

from engine.regex.derivative import matches
from engine.regex.parser import parse
from tests.engine.helpers import all_strings


@pytest.mark.parametrize(
    ("expression", "accepted"),
    [
        ("∅", {"" : False, "a": False}),
        ("ε", {"": True, "a": False}),
        ("a", {"a": True, "": False, "aa": False}),
        ("a|b", {"a": True, "b": True, "ab": False}),
        ("ab", {"ab": True, "a": False}),
        ("a*", {"": True, "a": True, "aa": True, "b": False}),
        ("a*b*", {"": True, "a": True, "b": True, "aabbb": True, "ba": False}),
        ("(a|b)*abb", {"abb": True, "aabb": True, "ab": False, "babb": True}),
        ("(a|ε)b", {"b": True, "ab": True, "": False}),
        ("a?", {"": True, "a": True, "aa": False}),
    ],
)
def test_reference_matcher(expression: str, accepted: dict[str, bool]) -> None:
    node, _ = parse(expression)
    assert {value: matches(node, value) for value in accepted} == accepted


def test_all_strings_includes_empty_string() -> None:
    assert all_strings("ab", 1) == ["", "a", "b"]
