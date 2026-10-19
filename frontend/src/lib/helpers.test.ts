import { describe, expect, it } from "vitest";
import { layoutAutomaton } from "./layout";
import { regexTokens } from "./regexTokens";
import { edgesForStep } from "./simulationEdges";
import type { Automaton } from "./types";

const dfa: Automaton = {
  type: "dfa", alphabet: ["a"], states: ["q0", "q1"], start: "q0", accepting: ["q1"],
  transitions: [{ from: "q0", symbol: "a", to: "q1" }],
};

describe("frontend helpers", () => {
  it("lays out every state and transition", () => {
    const result = layoutAutomaton(dfa);
    expect(result.nodes).toHaveLength(2);
    expect(result.edges[0].source).toBe("q0");
  });

  it("tokenizes escapes and operators without evaluating regexes", () => {
    expect(regexTokens(String.raw`a\|b*`).map((token) => token.kind)).toEqual(["symbol", "symbol", "symbol", "star"]);
  });

  it("finds transitions used by a simulation step", () => {
    expect(edgesForStep(dfa, { index: 0, symbol: "a", before: ["q0"], after: ["q1"], via_epsilon: [], note: "" }))
      .toEqual(["q0:a->q1"]);
  });
});
