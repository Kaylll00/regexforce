from engine.steps import Step
from engine.util import cap_steps, natural_sorted


def test_natural_sorted_orders_numeric_suffixes() -> None:
    assert natural_sorted(["q10", "q2", "q1"]) == ["q1", "q2", "q10"]


def test_cap_steps_keeps_499_and_adds_warning() -> None:
    steps = [Step(str(index), "description", {}) for index in range(501)]

    capped = cap_steps(steps)

    assert len(capped) == 500
    assert capped[-1].title == "Output truncated"
    assert capped[-1].kind == "warning"
