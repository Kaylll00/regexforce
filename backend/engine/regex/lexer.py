"""Lexer for the classical regular-expression syntax."""

from __future__ import annotations

from dataclasses import dataclass

from engine.errors import RegexSyntaxError, UnsupportedFeatureError


@dataclass(frozen=True)
class Token:
    """A lexical token with source offsets."""

    kind: str
    value: str
    start: int
    end: int


_UNSUPPORTED = frozenset(".[]{}^$")


def tokenize(text: str, *, textbook: bool = False) -> list[Token]:
    """Tokenize a regex and reject features outside classical regex syntax."""
    tokens: list[Token] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in " \t":
            index += 1
            continue
        if char in _UNSUPPORTED:
            raise UnsupportedFeatureError(
                f"'{char}' is outside classical regular expressions; escape it for a literal symbol.",
                index,
            )
        if char == "\\":
            if index + 1 >= len(text):
                raise RegexSyntaxError("Trailing backslash.", index)
            escaped = text[index + 1]
            if escaped.isdigit() and escaped != "0":
                raise UnsupportedFeatureError(
                    "Backreferences are outside classical regular expressions; use a literal or a regular-language construction.",
                    index,
                )
            kind = "epsilon" if escaped == "e" else "empty" if escaped == "0" else "symbol"
            tokens.append(Token(kind, escaped, index, index + 2))
            index += 2
            continue
        if char == "(":
            if index + 1 < len(text) and text[index + 1] == "?":
                raise UnsupportedFeatureError(
                    "Groups beginning with '(?' are outside classical regular expressions; use ordinary grouping instead.",
                    index,
                )
            tokens.append(Token("lparen", char, index, index + 1))
        elif char == ")":
            tokens.append(Token("rparen", char, index, index + 1))
        elif char == "|":
            tokens.append(Token("union", char, index, index + 1))
        elif char == "*":
            tokens.append(Token("star", char, index, index + 1))
        elif char == "+":
            tokens.append(Token("union" if textbook else "plus", char, index, index + 1))
        elif char == "?":
            tokens.append(Token("qmark", char, index, index + 1))
        elif char == "ε":
            tokens.append(Token("epsilon", char, index, index + 1))
        elif char == "∅":
            tokens.append(Token("empty", char, index, index + 1))
        else:
            tokens.append(Token("symbol", char, index, index + 1))
        index += 1

        if tokens and tokens[-1].kind in {"star", "plus", "qmark"} and index < len(text):
            next_char = text[index]
            if next_char == "?" or (next_char == "+" and not textbook):
                raise UnsupportedFeatureError(
                    "Lazy and possessive quantifiers are outside classical regular expressions; "
                    "use ordinary star, union, or grouping instead.",
                    index,
                )
    return tokens
