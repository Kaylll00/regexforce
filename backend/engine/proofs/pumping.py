"""Finite Pumping Lemma decomposition checks."""

from __future__ import annotations

from dataclasses import dataclass

from engine.errors import EngineError, LimitError
from engine.proofs.templates import Template
from engine.steps import Step

DISCLAIMER = (
    "The Pumping Lemma gives a necessary condition for regular languages. It can be used to show that a language is not regular. "
    "Failing or passing a pumping attempt never proves a language is regular, and testing many strings never establishes regularity."
)


@dataclass(frozen=True)
class Decomposition:
    x: str
    y: str
    z: str
    x_len: int
    y_len: int


@dataclass(frozen=True)
class DecompositionCheck:
    decomposition: Decomposition
    i: int
    pumped: str
    in_language: bool
    steps: list[Step]


@dataclass(frozen=True)
class PumpingReport:
    p: int
    string: str
    total: int
    refuted: int
    survivors: list[Decomposition]
    witness_i: dict[str, int]
    steps: list[Step]
    disclaimer: str


def validate_choice(template: Template, p: int, string: str) -> list[str]:
    problems = []
    if p < 1 or p > 12:
        problems.append("p must be between 1 and 12.")
    if len(string) > 200:
        problems.append("The string must be at most 200 characters.")
    if any(char not in template.alphabet for char in string):
        problems.append(f"The string may only use: {', '.join(template.alphabet)}.")
    if not template.membership(string):
        problems.append("The chosen string is not in the selected language.")
    if len(string) < p:
        problems.append("The chosen string must have length at least p.")
    return problems


def decompositions(string: str, p: int) -> list[Decomposition]:
    if p < 1 or len(string) < p:
        return []
    return [
        Decomposition(string[:x_len], string[x_len:x_len + y_len], string[x_len + y_len:], x_len, y_len)
        for x_len in range(min(p, len(string)))
        for y_len in range(1, min(p - x_len, len(string) - x_len) + 1)
    ]


def check_decomposition(template: Template, string: str, x_len: int, y_len: int, i: int) -> DecompositionCheck:
    if i < 0 or i > 8:
        raise LimitError("i must be between 0 and 8.")
    parts = decompositions(string, max(x_len + y_len, 1))
    decomposition = next((item for item in parts if item.x_len == x_len and item.y_len == y_len), None)
    if decomposition is None:
        raise EngineError("The decomposition must satisfy |xy| ≤ p and |y| ≥ 1.")
    pumped = decomposition.x + decomposition.y * i + decomposition.z
    return DecompositionCheck(decomposition, i, pumped, template.membership(pumped), [
        Step("Pump the selected decomposition", f"x y^{i} z = {pumped or 'ε'}.", {"pumped": pumped, "i": i}, "numeric_demonstration")
    ])


def check_all(template: Template, string: str, p: int, max_i: int = 5) -> PumpingReport:
    choices = decompositions(string, p)
    survivors = []
    witness_i: dict[str, int] = {}
    steps = []
    for decomposition in choices:
        found = None
        for i in range(max_i + 1):
            pumped = decomposition.x + decomposition.y * i + decomposition.z
            if not template.membership(pumped):
                found = i
                break
        key = f"{decomposition.x_len}:{decomposition.y_len}"
        if found is None:
            survivors.append(decomposition)
        else:
            witness_i[key] = found
        steps.append(Step("Check decomposition", f"x={decomposition.x or 'ε'}, y={decomposition.y}, z={decomposition.z or 'ε'}", {"x_len": decomposition.x_len, "y_len": decomposition.y_len, "witness_i": found}, "numeric_demonstration"))
    if survivors:
        conclusion = "This chosen string does not give a contradiction; this proves nothing about regularity."
    else:
        conclusion = "For this specific p every decomposition was pumped out of L; a complete proof requires the symbolic argument for arbitrary p."
    steps.append(Step("Numeric conclusion", conclusion, {"total": len(choices), "refuted": len(choices) - len(survivors)}, "numeric_demonstration"))
    return PumpingReport(p, string, len(choices), len(choices) - len(survivors), survivors, witness_i, steps, DISCLAIMER)
