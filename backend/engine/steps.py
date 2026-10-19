"""Explainable algorithm step data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Step:
    """One plain-English, JSON-serializable explanation of an algorithm."""

    title: str
    description: str
    data: dict[str, Any]
    kind: str = "info"

    def to_dict(self) -> dict[str, Any]:
        """Return the step in the shape used by the API."""
        return {
            "title": self.title,
            "description": self.description,
            "data": self.data,
            "kind": self.kind,
        }
