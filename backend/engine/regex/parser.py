"""Recursive-descent parser for classical regular expressions."""

from __future__ import annotations

from engine.errors import RegexSyntaxError
from engine.regex.ast import Concat, Empty, Epsilon, Node, Star, Symbol, Union
from engine.regex.lexer import Token, tokenize
from engine.steps import Step
from engine.util import cap_steps


def parse(text: str, *, textbook: bool = False) -> tuple[Node, list[Step]]:
    """Parse a regex using union, concatenation, grouping, and Kleene star."""
    tokens = tokenize(text, textbook=textbook)
    if not tokens:
        raise RegexSyntaxError("Empty regular expression.", 0)
    parser = _Parser(tokens, text)
    node = parser.parse_union()
    if parser.position != len(tokens):
        token = tokens[parser.position]
        raise RegexSyntaxError(f"Unexpected '{token.value}' at position {token.start}.", token.start)
    return node, cap_steps(parser.steps)


class _Parser:
    def __init__(self, tokens: list[Token], source: str) -> None:
        self.tokens = tokens
        self.source = source
        self.position = 0
        self.steps: list[Step] = []

    def parse_union(self) -> Node:
        node = self.parse_concat()
        while self._match("union"):
            operator = self.tokens[self.position - 1]
            if self._at_end() or self._peek().kind in {"union", "rparen"}:
                raise RegexSyntaxError("Empty operand after union.", operator.start)
            right = self.parse_concat()
            node = Union(node, right)
        return node

    def parse_concat(self) -> Node:
        if self._at_end() or self._peek().kind in {"union", "rparen"}:
            token = self._peek() if not self._at_end() else None
            position = token.start if token else len(self.source)
            raise RegexSyntaxError("Empty operand.", position)
        node = self.parse_postfix()
        while not self._at_end() and self._peek().kind not in {"union", "rparen"}:
            node = Concat(node, self.parse_postfix())
        return node

    def parse_postfix(self) -> Node:
        node = self.parse_atom()
        while not self._at_end() and self._peek().kind in {"star", "plus", "qmark"}:
            token = self.tokens[self.position]
            self.position += 1
            if token.kind == "star":
                node = Star(node)
            elif token.kind == "plus":
                node = Concat(node, Star(node))
                self.steps.append(
                    Step("Desugar +", "Rewrite one-or-more as one copy followed by Kleene star.", {})
                )
            else:
                node = Union(node, Epsilon())
                self.steps.append(
                    Step("Desugar ?", "Rewrite optionality as a union with ε.", {})
                )
        return node

    def parse_atom(self) -> Node:
        if self._at_end():
            raise RegexSyntaxError("Empty operand.", len(self.source))
        token = self.tokens[self.position]
        self.position += 1
        if token.kind == "symbol":
            return Symbol(token.value)
        if token.kind == "epsilon":
            return Epsilon()
        if token.kind == "empty":
            return Empty()
        if token.kind == "lparen":
            if self._at_end() or self._peek().kind == "rparen":
                raise RegexSyntaxError("Empty group.", token.start)
            node = self.parse_union()
            if self._at_end() or self._peek().kind != "rparen":
                raise RegexSyntaxError(f"Unmatched '(' at position {token.start}.", token.start)
            self.position += 1
            return node
        if token.kind == "rparen":
            raise RegexSyntaxError(f"Unmatched ')' at position {token.start}.", token.start)
        raise RegexSyntaxError(f"Unexpected '{token.value}' at position {token.start}.", token.start)

    def _at_end(self) -> bool:
        return self.position >= len(self.tokens)

    def _peek(self) -> Token:
        return self.tokens[self.position]

    def _match(self, kind: str) -> bool:
        if not self._at_end() and self._peek().kind == kind:
            self.position += 1
            return True
        return False
