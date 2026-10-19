import { create } from "zustand";
import type { Automaton } from "./types";

export const exampleAutomaton: Automaton = {
  type: "nfa",
  alphabet: ["a", "b"],
  states: ["q0", "q1"],
  start: "q0",
  accepting: ["q1"],
  transitions: [
    { from: "q0", symbol: "a", to: "q1" },
    { from: "q1", symbol: "b", to: "q1" },
  ],
};

type LabState = {
  automaton: Automaton;
  selectedState: string | null;
  result: { automaton?: Automaton; table?: unknown; steps?: unknown[]; regex?: string } | null;
  dirty: boolean;
  setAutomaton: (automaton: Automaton) => void;
  selectState: (state: string | null) => void;
  setResult: (result: LabState["result"]) => void;
  markExported: () => void;
};

export const useLabStore = create<LabState>((set) => ({
  automaton: exampleAutomaton,
  selectedState: "q0",
  result: null,
  dirty: false,
  setAutomaton: (automaton) => set({ automaton, dirty: true }),
  selectState: (selectedState) => set({ selectedState }),
  setResult: (result) => set({ result }),
  markExported: () => set({ dirty: false }),
}));
