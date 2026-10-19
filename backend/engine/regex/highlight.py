"""Non-throwing tokenization for editor highlighting."""

from __future__ import annotations

from engine.errors import EngineError
from engine.regex.lexer import Token, tokenize


def highlight_tokens(text: str, *, textbook: bool = False) -> list[Token]:
    """Return tokens for highlighting, converting invalid input to error tokens."""
    try:
        return tokenize(text, textbook=textbook)
    except EngineError:
        tokens: list[Token] = []
        index = 0
        while index < len(text):
            char = text[index]
            if char in " \t":
                index += 1
                continue
            try:
                candidate = tokenize(char, textbook=textbook)
            except EngineError:
                tokens.append(Token("error", char, index, index + 1))
            else:
                tokens.extend(
                    Token(token.kind, token.value, index + token.start, index + token.end)
                    for token in candidate
                )
            index += 1
        return tokens
