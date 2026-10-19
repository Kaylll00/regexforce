import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DerivationViewer } from "./DerivationViewer";

describe("DerivationViewer", () => {
  it("renders each derivation form", () => {
    render(<DerivationViewer accepted forms={["S", "aA", "ab"]} />);
    expect(screen.getByText("aA")).toBeInTheDocument();
    expect(screen.getByText("ab")).toBeInTheDocument();
  });

  it("renders a clear failure message", () => {
    render(<DerivationViewer accepted={false} forms={null} />);
    expect(screen.getByText(/not derivable/i)).toBeInTheDocument();
  });
});
