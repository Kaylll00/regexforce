"""Exceptions raised by the RegexForge engine."""

from __future__ import annotations


class EngineError(Exception):
    """Base class for errors produced by the formal-language engine."""

    code = "engine_error"

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.position = position


class RegexSyntaxError(EngineError):
    """A regex cannot be parsed because its syntax is invalid."""

    code = "regex_syntax"


class UnsupportedFeatureError(EngineError):
    """A regex uses a feature outside classical regular expressions."""

    code = "unsupported_feature"


class AutomatonError(EngineError):
    """An automaton is structurally invalid."""

    code = "automaton_invalid"


class GrammarError(EngineError):
    """A grammar is structurally invalid."""

    code = "grammar_invalid"


class LimitError(EngineError):
    """An engine safety limit was exceeded."""

    code = "limit_exceeded"
