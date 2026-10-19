import { describe, expect, it } from "vitest";
import { ApiError } from "./api";

describe("grammar error mapping", () => {
  it("preserves grammar error line numbers", () => {
    const error = new ApiError("A production must contain -> or →.", "grammar_invalid", 3);
    expect(error.code).toBe("grammar_invalid");
    expect(error.position).toBe(3);
  });
});
