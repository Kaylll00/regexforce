import { describe, expect, it } from "vitest";
import { addState, addTransition, checkDeterminism, removeState, removeTransition, renameState, setStart, setType, toggleAccepting } from "./automatonEdit";
import { exampleAutomaton } from "./labStore";

describe("automaton editing", () => {
  it("adds and removes states", () => {
    const edited = addState(exampleAutomaton, "q2");
    expect(edited.states).toContain("q2");
    expect(removeState(edited, "q2").states).not.toContain("q2");
  });
  it("renames, starts, and toggles accepting states", () => {
    const renamed = renameState(exampleAutomaton, "q1", "final");
    expect(setStart(renamed, "final").start).toBe("final");
    expect(toggleAccepting(renamed, "final").accepting).toEqual([]);
  });
  it("maintains alphabet from transitions", () => {
    const added = addTransition(exampleAutomaton, "q1", "q0", "c");
    expect(added.alphabet).toContain("c");
    expect(removeTransition(added, "q1", "q0", "c").alphabet).not.toContain("c");
  });
  it("reports DFA conflicts", () => {
    const withState = addState(exampleAutomaton, "q2");
    const dfa = setType(addTransition(addTransition(withState, "q0", "q1", "c"), "q0", "q2", "c"), "dfa");
    expect(checkDeterminism(dfa)).toHaveLength(1);
  });
});
