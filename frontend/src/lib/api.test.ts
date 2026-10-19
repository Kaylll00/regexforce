import { describe, expect, it, vi } from "vitest";
import { ApiError, apiPost } from "./api";

describe("API error mapping", () => {
  it("maps structured backend errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ error: { code: "automaton_invalid", message: "Bad transition", position: null } }),
      { status: 422, headers: { "Content-Type": "application/json" } },
    )));
    await expect(apiPost("/api/automata/validate", {})).rejects.toMatchObject({
      name: "ApiError", code: "automaton_invalid", message: "Bad transition",
    } satisfies Partial<ApiError>);
    vi.unstubAllGlobals();
  });
});
