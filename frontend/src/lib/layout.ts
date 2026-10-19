import type { Automaton } from "./types";

export type GraphNode = { id: string; x: number; y: number };
export type GraphEdge = { id: string; source: string; target: string; label: string };

export function layoutAutomaton(automaton: Automaton): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const depth = new Map<string, number>([[automaton.start, 0]]);
  const queue = [automaton.start];
  while (queue.length > 0) {
    const state = queue.shift() as string;
    for (const transition of automaton.transitions.filter((item) => item.from === state)) {
      if (!depth.has(transition.to)) {
        depth.set(transition.to, (depth.get(state) ?? 0) + 1);
        queue.push(transition.to);
      }
    }
  }
  const maxDepth = Math.max(0, ...Array.from(depth.values()));
  const nodes = automaton.states.map((state) => {
    const column = depth.get(state) ?? maxDepth + 1;
    const row = automaton.states.filter((item) => (depth.get(item) ?? maxDepth + 1) === column).indexOf(state);
    return { id: state, x: column * 180 + 80, y: row * 100 + 60 };
  });
  const edges = automaton.transitions.map((transition, index) => ({
    id: `${transition.from}-${transition.to}-${index}`,
    source: transition.from,
    target: transition.to,
    label: transition.symbol,
  }));
  return { nodes, edges };
}
