"""Shared deterministic ordering and safety helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TypeVar

from engine.steps import Step

T = TypeVar("T")
_NATURAL_PARTS = re.compile(r"(\d+)")


def natural_sorted(items: Iterable[T]) -> list[T]:
    """Sort strings naturally, placing q2 before q10."""
    return sorted(items, key=_natural_key)


def _natural_key(value: T) -> tuple[object, ...]:
    text = str(value)
    return tuple(
        int(part) if part.isdigit() else part.casefold()
        for part in _NATURAL_PARTS.split(text)
    )


def cap_steps(steps: Iterable[Step]) -> list[Step]:
    """Keep at most 500 steps and mark output that was truncated."""
    result = list(steps)
    if len(result) <= 500:
        return result
    return [
        *result[:499],
        Step(
            title="Output truncated",
            description="The operation produced more than 500 steps, so only the first 499 are shown.",
            data={},
            kind="warning",
        ),
    ]
