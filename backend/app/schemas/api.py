"""Pydantic request models and validation limits."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class RegexRequest(BaseModel):
    regex: str = Field(max_length=500)
    textbook: bool = False
    alphabet: list[str] | None = Field(default=None, max_length=64)

    @field_validator("alphabet")
    @classmethod
    def valid_alphabet(cls, value):
        if value is not None and any(len(item) != 1 for item in value):
            raise ValueError("alphabet entries must be single characters")
        return value


class AutomatonRequest(BaseModel):
    automaton: dict[str, Any]


class SimulateRequest(AutomatonRequest):
    strings: list[str] = Field(max_length=500)

    @field_validator("strings")
    @classmethod
    def valid_strings(cls, value):
        if any(len(item) > 200 for item in value):
            raise ValueError("strings must be at most 200 characters")
        return value


class GrammarRequest(BaseModel):
    grammar: str = Field(max_length=5000)


class RuleRequest(BaseModel):
    rule: dict[str, Any]
    alphabet: list[str] | None = Field(default=None, max_length=64)


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class RuleInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kind: str
    definition: dict[str, Any]


class TestSetInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    strings: list[dict[str, Any]] = Field(max_length=500)
