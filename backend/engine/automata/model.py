"""Validated NFA and DFA data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias

from engine.errors import AutomatonError
from engine.util import natural_sorted

EPSILON = "ε"


@dataclass(frozen=True)
class NFA:
    states: frozenset[str]
    alphabet: frozenset[str]
    start: str
    accepting: frozenset[str]
    transitions: dict[tuple[str, str], frozenset[str]]
    labels: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def validate(self) -> None:
        """Reject invalid states, transitions, and alphabet entries."""
        _validate_common(self.states, self.alphabet, self.start, self.accepting)
        for (source, symbol), targets in self.transitions.items():
            if source not in self.states or not targets.issubset(self.states):
                raise AutomatonError("A transition references an unknown state.")
            if symbol != EPSILON and symbol not in self.alphabet:
                raise AutomatonError("A transition uses a symbol outside the alphabet.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize this NFA in the public automaton JSON format."""
        self.validate()
        transitions = [
            {"from": source, "symbol": symbol, "to": target}
            for (source, symbol), targets in self.transitions.items()
            for target in natural_sorted(targets)
        ]
        transitions.sort(key=lambda item: (natural_sorted([item["from"]])[0], item["symbol"] != EPSILON,
                                            item["symbol"], item["to"]))
        return _to_dict(self, "nfa", transitions)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NFA:
        """Deserialize and validate an NFA."""
        parsed = _parse_common(data, "nfa")
        transitions = _parse_transitions(data, parsed["states"], parsed["alphabet"], True)
        result = cls(**parsed, transitions=transitions)
        result.validate()
        return result


@dataclass(frozen=True)
class DFA:
    states: frozenset[str]
    alphabet: frozenset[str]
    start: str
    accepting: frozenset[str]
    transitions: dict[tuple[str, str], str]
    labels: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def validate(self) -> None:
        """Reject invalid states, transitions, and epsilon edges."""
        _validate_common(self.states, self.alphabet, self.start, self.accepting)
        for (source, symbol), target in self.transitions.items():
            if source not in self.states or target not in self.states:
                raise AutomatonError("A transition references an unknown state.")
            if symbol == EPSILON:
                raise AutomatonError("A DFA cannot contain ε transitions.")
            if symbol not in self.alphabet:
                raise AutomatonError("A transition uses a symbol outside the alphabet.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize this DFA in the public automaton JSON format."""
        self.validate()
        transitions = [
            {"from": source, "symbol": symbol, "to": target}
            for (source, symbol), target in self.transitions.items()
        ]
        transitions.sort(key=lambda item: (item["from"], item["symbol"], item["to"]))
        return _to_dict(self, "dfa", transitions)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DFA:
        """Deserialize and validate a DFA."""
        parsed = _parse_common(data, "dfa")
        transitions = _parse_transitions(data, parsed["states"], parsed["alphabet"], False)
        result = cls(**parsed, transitions=transitions)
        result.validate()
        return result


Automaton: TypeAlias = NFA | DFA


def transition_table(automaton: Automaton) -> dict[str, Any]:
    """Return a deterministic tabular view of an NFA or DFA."""
    automaton.validate()
    has_epsilon = isinstance(automaton, NFA) and any(
        symbol == EPSILON for _, symbol in automaton.transitions
    )
    alphabet = natural_sorted(automaton.alphabet)
    columns = [*alphabet, EPSILON] if has_epsilon else alphabet
    rows = []
    for state in natural_sorted(automaton.states):
        cells: dict[str, list[str]] = {}
        for symbol in columns:
            value = automaton.transitions.get((state, symbol))
            if isinstance(automaton, NFA):
                cells[symbol] = natural_sorted(value if isinstance(value, frozenset) else ())
            else:
                target = value if isinstance(value, str) else None
                cells[symbol] = [] if target is None else [target]
        rows.append({
            "state": state,
            "start": state == automaton.start,
            "accepting": state in automaton.accepting,
            "cells": cells,
        })
    return {"alphabet": alphabet, "has_epsilon": has_epsilon, "rows": rows}


def _validate_common(states, alphabet, start, accepting) -> None:
    if start not in states:
        raise AutomatonError("The start state must belong to states.")
    if not accepting.issubset(states):
        raise AutomatonError("Accepting states must belong to states.")


def _to_dict(automaton, kind, transitions) -> dict[str, Any]:
    return {
        "type": kind,
        "alphabet": natural_sorted(automaton.alphabet),
        "states": natural_sorted(automaton.states),
        "start": automaton.start,
        "accepting": natural_sorted(automaton.accepting),
        "transitions": transitions,
        "labels": {
            state: list(automaton.labels[state])
            for state in natural_sorted(automaton.labels)
        },
    }


def _parse_common(data: dict[str, Any], expected: str) -> dict[str, Any]:
    required = {"type", "alphabet", "states", "start", "accepting", "transitions"}
    if not required.issubset(data):
        raise AutomatonError("Automaton JSON is missing required keys.")
    if data["type"] != expected:
        raise AutomatonError(f"Expected an {expected.upper()} automaton.")
    states = data["states"]
    alphabet = data["alphabet"]
    if not isinstance(states, list) or len(states) != len(set(states)) or not all(
        isinstance(item, str) for item in states
    ):
        raise AutomatonError("States must be a list of unique strings.")
    if not isinstance(alphabet, list) or not all(
        isinstance(item, str) and len(item) == 1 and item != EPSILON for item in alphabet
    ):
        raise AutomatonError("Alphabet must contain single-character strings other than ε.")
    return {
        "states": frozenset(states),
        "alphabet": frozenset(alphabet),
        "start": data["start"],
        "accepting": frozenset(data["accepting"]),
        "labels": _parse_labels(data.get("labels", {})),
    }


def _parse_labels(labels: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(labels, dict):
        raise AutomatonError("Labels must be an object.")
    return {
        state: tuple(value)
        for state, value in labels.items()
        if isinstance(state, str) and isinstance(value, list) and all(isinstance(v, str) for v in value)
    }


def _parse_transitions(data, states, alphabet, is_nfa):
    raw = data["transitions"]
    if not isinstance(raw, list):
        raise AutomatonError("Transitions must be a list.")
    result = {}
    for item in raw:
        if not isinstance(item, dict) or not {"from", "symbol", "to"}.issubset(item):
            raise AutomatonError("Each transition needs from, symbol, and to.")
        source, symbol, target = item["from"], item["symbol"], item["to"]
        if source not in states or target not in states:
            raise AutomatonError("A transition references an unknown state.")
        if symbol != EPSILON and symbol not in alphabet:
            raise AutomatonError("A transition uses a symbol outside the alphabet.")
        key = (source, symbol)
        if is_nfa:
            result[key] = frozenset(set(result.get(key, frozenset())) | {target})
        else:
            if key in result:
                raise AutomatonError("A DFA cannot have two targets for one state and symbol.")
            result[key] = target
    return result
