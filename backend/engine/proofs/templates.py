"""Guided language templates for Pumping Lemma demonstrations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from engine.steps import Step


@dataclass(frozen=True)
class Template:
    id: str
    name: str
    description: str
    alphabet: tuple[str, ...]
    is_regular: bool
    membership: Callable[[str], bool]
    witness: Callable[[int], str]
    outline: tuple[Step, ...]


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    return all(value % divisor for divisor in range(2, int(value**0.5) + 1))


def _templates() -> tuple[Template, ...]:
    valid = "This symbolic outline is a proof pattern; numeric checks alone never prove regularity."
    return (
        Template("anbn", "{aⁿbⁿ | n ≥ 0}", "Equal numbers of a symbols followed by b symbols.", ("a", "b"), False,
                  lambda s: s == "a" * s.count("a") + "b" * s.count("b") and s.count("a") == s.count("b"), lambda p: "a" * p + "b" * p,
                  (Step("Choose the witness", "Let s = a^p b^p.", {}, "valid_argument"), Step("Pump any nonempty y", valid, {}, "valid_argument"))),
        Template("ww", "{ww | w ∈ {a,b}*}", "Two identical copies of a word.", ("a", "b"), False,
                  lambda s: len(s) % 2 == 0 and s[:len(s)//2] == s[len(s)//2:], lambda p: "a" * p + "b" + "a" * p + "b",
                  (Step("Choose the witness", "Let s = a^p b a^p b.", {}, "valid_argument"), Step("Case-analyse y", valid, {}, "valid_argument"))),
        Template("prime", "{aⁿ | n is prime}", "Unary strings whose length is prime.", ("a",), False,
                  lambda s: all(char == "a" for char in s) and _is_prime(len(s)), lambda p: "a" * next(q for q in range(p, p + 100) if _is_prime(q)),
                  (Step("Choose a prime length", "Choose q as the smallest prime q ≥ p.", {}, "valid_argument"), Step("Pump", valid, {}, "valid_argument"))),
        Template("square", "{a^(n²) | n ≥ 0}", "Unary strings whose length is a perfect square.", ("a",), False,
                  lambda s: all(char == "a" for char in s) and int(len(s) ** 0.5) ** 2 == len(s), lambda p: "a" * (p * p),
                  (Step("Choose the witness", "Let s = a^(p²).", {}, "valid_argument"), Step("Pump", valid, {}, "valid_argument"))),
        Template("balanced", "Balanced parentheses", "Balanced parentheses over {(, )}.", ("(", ")"), False,
                  lambda s: _balanced(s), lambda p: "(" * p + ")" * p,
                  (Step("Choose the witness", "Let s = (^p )^p.", {}, "valid_argument"), Step("Pump", valid, {}, "valid_argument"))),
        Template("abstar", "(ab)*", "A regular demonstration language.", ("a", "b"), True,
                  lambda s: len(s) % 2 == 0 and all(s[index:index + 2] == "ab" for index in range(0, len(s), 2)), lambda p: "ab" * p,
                  (Step("Regular-language demonstration", "Pumping attempts may survive for a regular language.", {}, "valid_argument"),)),
    )


def _balanced(value: str) -> bool:
    depth = 0
    for char in value:
        depth += 1 if char == "(" else -1 if char == ")" else -1000
        if depth < 0:
            return False
    return depth == 0


TEMPLATES = _templates()


def list_templates() -> list[Template]:
    return list(TEMPLATES)


def get_template(template_id: str) -> Template:
    for template in TEMPLATES:
        if template.id == template_id:
            return template
    raise ValueError(f"Unknown proof template: {template_id}.")
