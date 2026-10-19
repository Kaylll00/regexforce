"""PDF and CSV report generation."""

from __future__ import annotations

import csv
import io
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas

from app.services.engine_service import build_regex


def build_pdf(payload: dict[str, Any]) -> bytes:
    result = build_regex(payload["regex"], bool(payload.get("textbook", False)), payload.get("alphabet"))
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=letter)
    y = 760
    canvas.setTitle(payload.get("title", "RegexForge report"))

    def line(text: str, size: int = 10) -> None:
        nonlocal y
        if y < 50:
            canvas.showPage()
            y = 760
        canvas.setFont("Helvetica", size)
        canvas.drawString(45, y, text[:115])
        y -= size + 5

    line(payload.get("title", "RegexForge report"), 16)
    line(f"Regex: {payload['regex']}")
    line(f"Canonical: {result['canonical']}")
    line(f"Alphabet: {', '.join(result['alphabet']) or 'empty'}")
    for stage in ("nfa", "dfa", "min_dfa"):
        automaton = result[stage]
        line(f"{stage.upper()} states: {', '.join(automaton['states'])}")
        line(f"Accepting: {', '.join(automaton['accepting']) or 'none'}")
        for transition in automaton["transitions"][:30]:
            line(f"  {transition['from']} --{transition['symbol']}--> {transition['to']}")
    if payload.get("strings"):
        line("Test results", 12)
        for item in payload["strings"]:
            line(f"  {item.get('value', '')!r} expected={item.get('expected', 'unspecified')}")
    canvas.save()
    return stream.getvalue()


def build_csv(payload: dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    if payload.get("kind") == "tests":
        writer.writerow(["string", "expected", "actual", "match"])
        for item in payload.get("strings", []):
            writer.writerow([item.get("value", ""), item.get("expected", ""), item.get("actual", ""), item.get("match", "")])
    else:
        writer.writerow(["state", "symbol", "target"])
        for transition in payload.get("automaton", {}).get("transitions", []):
            writer.writerow([transition["from"], transition["symbol"], transition["to"]])
    return output.getvalue()
