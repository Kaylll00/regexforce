"""Comparison reports for multiple named rules."""

from __future__ import annotations

from dataclasses import dataclass

from engine.analysis.properties import compare, is_subset
from engine.automata.model import DFA


@dataclass(frozen=True)
class ComparisonReport:
    """Pairwise language relationships and redundant rule names."""

    matrix: list[list[dict[str, object]]]
    redundant: list[str]


def compare_many(rules: list[tuple[str, DFA]]) -> ComparisonReport:
    """Compare every pair and flag rules covered by an earlier/larger rule."""
    matrix: list[list[dict[str, object]]] = []
    redundant: list[str] = []
    for index, (name, dfa) in enumerate(rules):
        row: list[dict[str, object]] = []
        for other_index, (other_name, other_dfa) in enumerate(rules):
            relation = compare(dfa, other_dfa)
            row.append({"rule": other_name, "relation": relation.relation, "witnesses": relation.witnesses})
            subset, _ = is_subset(dfa, other_dfa)
            equal, _ = is_subset(other_dfa, dfa)
            if index != other_index and subset and (not equal or other_index < index) and name not in redundant:
                redundant.append(name)
        matrix.append(row)
    return ComparisonReport(matrix, redundant)
