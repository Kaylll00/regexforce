import type { Automaton, SimStep } from "./types";

export function edgesForStep(automaton: Automaton, step: SimStep): string[] {
  if (step.symbol === null) return [];
  const edges = automaton.transitions.filter(
    (transition) => transition.symbol === step.symbol && step.before.includes(transition.from) && step.after.includes(transition.to),
  );
  return edges.map((edge) => `${edge.from}:${edge.symbol}->${edge.to}`);
}
