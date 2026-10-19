import { describe, expect, it } from "vitest";
import { exampleAutomaton, useLabStore } from "./labStore";

describe("lab store", () => {
  it("tracks selection, result, and export state", () => {
    useLabStore.getState().setAutomaton(exampleAutomaton);
    useLabStore.getState().selectState("q1");
    useLabStore.getState().setResult({ regex: "a", steps: [] });
    expect(useLabStore.getState().selectedState).toBe("q1");
    expect(useLabStore.getState().result?.regex).toBe("a");
    expect(useLabStore.getState().dirty).toBe(true);
    useLabStore.getState().markExported();
    expect(useLabStore.getState().dirty).toBe(false);
  });
});
