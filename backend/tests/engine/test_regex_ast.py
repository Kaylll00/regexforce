from engine.regex.ast import Concat, Epsilon, Symbol, Union, alphabet_of, from_dict, to_dict


def test_ast_json_round_trip() -> None:
    node = Union(Concat(Symbol("a"), Epsilon()), Symbol("b"))
    assert from_dict(to_dict(node)) == node
    assert alphabet_of(node) == frozenset({"a", "b"})
