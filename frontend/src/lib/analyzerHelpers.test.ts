import { describe, expect, it } from "vitest";
import { relationClass, relationLabel } from "./analyzerHelpers";

describe("analyzer relation helpers", () => {
  it("maps relations to readable labels and colors", () => {
    expect(relationLabel("equivalent")).toBe("Equivalent");
    expect(relationClass("disjoint")).toContain("slate");
  });
});
