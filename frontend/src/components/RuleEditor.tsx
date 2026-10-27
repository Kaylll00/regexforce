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
  return <section className="min-w-0 rounded-2xl border border-slate-700/80 bg-slate-900/80 p-4 shadow-lg shadow-black/10">
    <div className="flex items-center justify-between gap-3"><h3 className="font-semibold">{label}</h3><select aria-label={`${label} type`} className="cursor-pointer rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-sm font-medium text-slate-100 hover:border-cyan-400 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/20" value={value.kind} onChange={(event) => changeKind(event.target.value as Rule["kind"])}><option value="regex">Regex</option><option value="automaton">Automaton JSON</option><option value="grammar">Grammar</option></select></div>
    <textarea aria-label={`${label} input`} className="mt-3 min-h-40 w-full resize-y rounded-xl border border-slate-700 bg-slate-950 p-3 font-mono text-sm leading-6 text-slate-100 placeholder:text-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/20" value={text} onChange={(event) => changeText(event.target.value)} placeholder={value.kind === "regex" ? "(a|b)*abb" : value.kind === "grammar" ? "S -> aS | ε" : "Automaton JSON"} />
  </section>;
}
