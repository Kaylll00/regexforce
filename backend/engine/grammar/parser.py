"""Parser for right-linear and left-linear grammars."""

from __future__ import annotations

from engine.errors import GrammarError
from engine.grammar.model import Grammar, Production
from engine.steps import Step


def parse_grammar(text: str) -> tuple[Grammar, list[Step]]:
    """Parse a regular grammar and infer whether it is right- or left-linear."""
    productions: list[Production] = []
    orientations: set[str] = set()
    start: str | None = None
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        separator = "->" if "->" in line else "→" if "→" in line else None
        if separator is None:
            raise GrammarError("A production must contain -> or →.", line_number)
        head_text, alternatives = line.split(separator, 1)
        head = head_text.strip()
        if len(head) != 1 or not head.isupper() or not head.isascii():
            raise GrammarError("Nonterminals must be single uppercase ASCII letters.", line_number)
        start = start or head
        for alternative in alternatives.split("|"):
            body_text = alternative.strip()
            if not body_text:
                raise GrammarError("A production alternative cannot be empty.", line_number)
            body = _parse_body(body_text, line_number)
            nonterminals = [index for index, symbol in enumerate(body) if _is_nonterminal(symbol)]
            if len(nonterminals) > 1:
                raise GrammarError("A regular production may contain at most one nonterminal.", line_number)
            if not nonterminals:
                orientation = None
            elif nonterminals[0] == len(body) - 1:
                orientation = "right-linear"
            elif nonterminals[0] == 0:
                orientation = "left-linear"
            else:
                raise GrammarError(
                    "The nonterminal must be at the beginning or end of a regular production.",
                    line_number,
                )
            if orientation is not None:
                orientations.add(orientation)
            productions.append(Production(head, body))
    if not productions or start is None:
        raise GrammarError("The grammar must contain at least one production.", 1)
    if len(orientations) > 1:
        raise GrammarError("Mixing left-linear and right-linear productions is not regular.", 1)
    kind = next(iter(orientations), "right-linear")
    return Grammar(start, tuple(productions), kind), [
        Step("Parse grammar", f"Parsed {len(productions)} regular productions.", {})
    ]


def _parse_body(text: str, line_number: int) -> tuple[str, ...]:
    if text in {"ε", r"\e"}:
        return ("ε",)
    body: list[str] = []
    index = 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        if text[index] == "\\" and index + 1 < len(text) and text[index + 1] == "e":
            body.append("ε")
            index += 2
            continue
        symbol = text[index]
        if symbol in {"|", "-", ">", "→", "#"} or symbol.isspace():
            raise GrammarError("Invalid terminal in production body.", line_number)
        body.append(symbol)
        index += 1
    if "ε" in body and body != ["ε"]:
        raise GrammarError("Epsilon must be the only symbol in a production body.", line_number)
    return tuple(body)


def _is_nonterminal(symbol: str) -> bool:
    return len(symbol) == 1 and symbol.isupper() and symbol.isascii()
