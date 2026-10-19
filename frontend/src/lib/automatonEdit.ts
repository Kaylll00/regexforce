import type { Automaton, Transition } from "./types";

const clone = (automaton: Automaton): Automaton => ({
  ...automaton,
  alphabet: [...automaton.alphabet],
  states: [...automaton.states],
  accepting: [...automaton.accepting],
  transitions: automaton.transitions.map((transition) => ({ ...transition })),
  labels: automaton.labels ? Object.fromEntries(Object.entries(automaton.labels).map(([key, value]) => [key, [...value]])) : undefined,
});

const withAlphabet = (automaton: Automaton, transitions: Transition[]): Automaton => ({
  ...automaton,
  transitions,
  alphabet: [...new Set(transitions.map((transition) => transition.symbol).filter((symbol) => symbol !== "ε"))].sort(),
});

export function addState(automaton: Automaton, state: string): Automaton {
  const result = clone(automaton);
  if (state && !result.states.includes(state)) result.states.push(state);
  return result;
}

export function removeState(automaton: Automaton, state: string): Automaton {
  const result = clone(automaton);
  if (result.states.length <= 1 || !result.states.includes(state)) return result;
  result.states = result.states.filter((item) => item !== state);
  result.accepting = result.accepting.filter((item) => item !== state);
  result.start = result.start === state ? result.states[0] : result.start;
  return withAlphabet(result, result.transitions.filter((transition) => transition.from !== state && transition.to !== state));
}

export function renameState(automaton: Automaton, state: string, nextState: string): Automaton {
  if (!nextState || state === nextState || automaton.states.includes(nextState)) return clone(automaton);
  const result = clone(automaton);
  result.states = result.states.map((item) => item === state ? nextState : item);
  result.start = result.start === state ? nextState : result.start;
  result.accepting = result.accepting.map((item) => item === state ? nextState : item);
  result.transitions = result.transitions.map((transition) => ({
    ...transition,
    from: transition.from === state ? nextState : transition.from,
    to: transition.to === state ? nextState : transition.to,
  }));
  return result;
}

export function setStart(automaton: Automaton, state: string): Automaton {
  return automaton.states.includes(state) ? { ...clone(automaton), start: state } : clone(automaton);
}

export function toggleAccepting(automaton: Automaton, state: string): Automaton {
  const result = clone(automaton);
  result.accepting = result.accepting.includes(state)
    ? result.accepting.filter((item) => item !== state)
    : [...result.accepting, state];
  return result;
}

export function addTransition(automaton: Automaton, from: string, to: string, symbol: string): Automaton {
  const normalized = symbol.trim();
  if (!automaton.states.includes(from) || !automaton.states.includes(to) || !normalized || automaton.transitions.some((item) => item.from === from && item.to === to && item.symbol === normalized)) return clone(automaton);
  return withAlphabet(clone(automaton), [...automaton.transitions, { from, to, symbol: normalized }]);
}

export function removeTransition(automaton: Automaton, from: string, to: string, symbol: string): Automaton {
  return withAlphabet(clone(automaton), automaton.transitions.filter((item) => !(item.from === from && item.to === to && item.symbol === symbol)));
}

export function setType(automaton: Automaton, type: "nfa" | "dfa"): Automaton {
  return { ...clone(automaton), type };
}

export function checkDeterminism(automaton: Automaton): string[] {
  const problems: string[] = [];
  const seen = new Set<string>();
  for (const transition of automaton.transitions) {
    if (transition.symbol === "ε") problems.push(`DFA cannot have an ε transition from ${transition.from}.`);
    const key = `${transition.from}\u0000${transition.symbol}`;
    if (seen.has(key)) problems.push(`DFA has multiple transitions from ${transition.from} on ${transition.symbol}.`);
    seen.add(key);
  }
  return problems;
}
