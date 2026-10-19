import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RuleEditor } from "./RuleEditor";
import type { Rule } from "@/lib/types";

describe("RuleEditor", () => {
  it("switches rule kind and input", () => {
    const onChange = (rule: Rule) => { expect(rule.kind).toBe("grammar"); };
    render(<RuleEditor value={{ kind: "regex", regex: "a" }} onChange={onChange} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "grammar" } });
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });
});
