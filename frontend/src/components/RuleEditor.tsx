"use client";

import { useState } from "react";
import type { Rule } from "@/lib/types";

type Props = { value: Rule; onChange: (rule: Rule) => void; label?: string };

export function RuleEditor({ value, onChange, label = "Rule" }: Props) {
  const [text, setText] = useState(value.kind === "regex" ? value.regex ?? "" : value.kind === "grammar" ? value.grammar ?? "" : JSON.stringify(value.automaton ?? {}, null, 2));
  function changeKind(kind: Rule["kind"]) {
    const next: Rule = kind === "regex" ? { kind, regex: "" } : kind === "grammar" ? { kind, grammar: "" } : { kind, automaton: { type: "dfa", alphabet: [], states: ["q0"], start: "q0", accepting: [], transitions: [] } };
    setText(kind === "automaton" ? JSON.stringify(next.automaton, null, 2) : "");
    onChange(next);
  }
  function changeText(nextText: string) {
    setText(nextText);
    if (value.kind === "regex") onChange({ ...value, regex: nextText });
    else if (value.kind === "grammar") onChange({ ...value, grammar: nextText });
    else {
      try { onChange({ ...value, automaton: JSON.parse(nextText) }); } catch { onChange(value); }
    }
  }
  return <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
    <div className="flex items-center justify-between gap-3"><h3 className="font-semibold">{label}</h3><select className="rounded bg-slate-800 p-2" value={value.kind} onChange={(event) => changeKind(event.target.value as Rule["kind"])}><option value="regex">Regex</option><option value="automaton">Automaton JSON</option><option value="grammar">Grammar</option></select></div>
    <textarea className="mt-3 min-h-28 w-full rounded bg-slate-950 p-3 font-mono text-sm" value={text} onChange={(event) => changeText(event.target.value)} placeholder={value.kind === "regex" ? "(a|b)*abb" : value.kind === "grammar" ? "S -> aS | ε" : "Automaton JSON"} />
  </section>;
}
