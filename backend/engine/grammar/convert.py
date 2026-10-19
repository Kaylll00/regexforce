"""Conversions between regular grammars, automata, and regexes."""

from __future__ import annotations

from collections import deque

from engine.automata.dfa_ops import minimize_dfa
from engine.automata.model import DFA, EPSILON, NFA
from engine.automata.nfa_ops import remove_epsilon, reverse_nfa
from engine.automata.subset import nfa_to_dfa
from engine.automata.thompson import regex_to_nfa
from engine.conversion.state_elimination import automaton_to_regex_state_elimination
from engine.errors import GrammarError
from engine.grammar.model import Grammar, Production
from engine.regex.ast import Node
from engine.steps import Step
from engine.util import natural_sorted


def grammar_to_nfa(grammar: Grammar) -> tuple[NFA, list[Step]]:
    """Build an NFA from a right- or left-linear grammar."""
    if grammar.kind == "left-linear":
        reversed_productions = tuple(
            Production(production.head, tuple(reversed(production.body)))
            for production in grammar.productions
        )
        right = Grammar(grammar.start, reversed_productions, "right-linear")
        nfa, right_steps = grammar_to_nfa(right)
        return reverse_nfa(nfa), [
            *right_steps,
            Step("Reverse left-linear grammar", "Reverse the right-linear construction to restore the original language.", {}),
        ]
    nonterminals = {production.head for production in grammar.productions}
    states = set(nonterminals) | {"F"}
    transitions: dict[tuple[str, str], set[str]] = {}
    counter = 0
    steps: list[Step] = []
    for production in grammar.productions:
        symbols = list(production.body)
        target = symbols.pop() if symbols and _is_nonterminal(symbols[-1]) else "F"
        current = production.head
        if not symbols:
            transitions.setdefault((current, EPSILON), set()).add(target)
        else:
            for index, symbol in enumerate(symbols):
                next_state = target if index == len(symbols) - 1 else f"{production.head}.p{counter}.{index}"
                if next_state == target:
                    states.add(next_state)
                else:
                    states.add(next_state)
                transitions.setdefault((current, symbol), set()).add(next_state)
                current = next_state
                counter += 1
        steps.append(Step(
            "Convert production",
            f"Add transitions for {production.head} -> {''.join(production.body)}.",
            {"production": f"{production.head} -> {''.join(production.body)}"},
        ))
    alphabet = frozenset(
        symbol for (source, symbol) in transitions if symbol != EPSILON
    )
    nfa = NFA(
        frozenset(states), alphabet, grammar.start, frozenset({"F"}),
        {key: frozenset(targets) for key, targets in transitions.items()},
    )
    nfa.validate()
    return nfa, steps


def nfa_to_grammar(a: NFA | DFA) -> tuple[Grammar, list[Step]]:
    """Convert an automaton to a named right-linear grammar."""
    nfa = a
    if isinstance(a, NFA) and any(symbol == EPSILON for _, symbol in a.transitions):
        nfa, steps = remove_epsilon(a)
    else:
        steps = []
    states = _bfs_states(nfa)
    if len(states) > 26:
        raise GrammarError("More than 26 states need names; minimize the automaton first.")
    if any(symbol.isupper() for symbol in nfa.alphabet):
        raise GrammarError("Uppercase alphabet symbols conflict with nonterminals; use a different alphabet.")
    names = {nfa.start: "S"}
    used = {"S"}
    next_letter = 0
    for state in states:
        if state == nfa.start:
            continue
        while chr(ord("A") + next_letter) == "S":
            next_letter += 1
        candidate = chr(ord("A") + next_letter)
        next_letter += 1
        names[state] = candidate
        used.add(candidate)
    productions: list[Production] = []
    for (source, symbol), targets in nfa.transitions.items():
        if symbol == EPSILON:
            continue
        target_set = targets if isinstance(targets, frozenset) else {targets}
        for target in natural_sorted(target_set):
            productions.append(Production(names[source], (symbol, names[target])))
    for state in natural_sorted(nfa.accepting):
        productions.append(Production(names[state], ("ε",)))
    grammar = Grammar("S", tuple(productions), "right-linear")
    return grammar, [*steps, Step("Convert automaton", "Name states in breadth-first order and create regular productions.", {})]


def grammar_to_regex(grammar: Grammar) -> tuple[Node, list[Step]]:
    """Convert a regular grammar through its NFA to a regex."""
    nfa, grammar_steps = grammar_to_nfa(grammar)
    regex, conversion_steps = automaton_to_regex_state_elimination(nfa)
    return regex, [*grammar_steps, *conversion_steps]


def regex_to_grammar(node: Node) -> tuple[Grammar, list[Step]]:
    """Convert a regex through a minimized DFA to a regular grammar."""
    nfa, nfa_steps = regex_to_nfa(node)
    dfa, subset_steps = nfa_to_dfa(nfa)
    minimum, minimum_steps = minimize_dfa(dfa)
    grammar, grammar_steps = nfa_to_grammar(minimum)
    return grammar, [*nfa_steps, *subset_steps, *minimum_steps, *grammar_steps]


def _bfs_states(nfa: NFA | DFA) -> list[str]:
    result: list[str] = []
    queue = deque([nfa.start])
    seen = {nfa.start}
    while queue:
        state = queue.popleft()
        result.append(state)
        for symbol in natural_sorted(nfa.alphabet):
            value = nfa.transitions.get((state, symbol))
            targets = value if isinstance(value, frozenset) else ({value} if value else set())
            for target in natural_sorted(targets):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
    return result


def _is_nonterminal(symbol: str) -> bool:
    return len(symbol) == 1 and symbol.isupper() and symbol.isascii()
