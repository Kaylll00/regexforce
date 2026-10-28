"use client";

import { useEffect, useState } from "react";
import { apiPost, ApiError, downloadPost } from "@/lib/api";
import type { Automaton, SimulationResult, Step, TransitionTable } from "@/lib/types";
import { AutomatonGraph } from "@/components/AutomatonGraph";
import { Disclaimer } from "@/components/Disclaimer";
import { StepsPanel } from "@/components/StepsPanel";
import { TransitionTable as AutomatonTable } from "@/components/TransitionTable";

type BuildResult = {
  canonical: string;
  alphabet: string[];
  nfa: Automaton;
  dfa: Automaton;
  min_dfa: Automaton;
  tables: { nfa: TransitionTable; dfa: TransitionTable; min_dfa: TransitionTable };
  steps_by_stage: Record<string, Step[]>;
};

export default function Studio() {
  const [regex, setRegex] = useState("a(b|c)*");
  const [textbook, setTextbook] = useState(false);
  const [build, setBuild] = useState<BuildResult | null>(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<"nfa" | "dfa" | "min_dfa">("min_dfa");
  const [testString, setTestString] = useState("");
  const [verdict, setVerdict] = useState<SimulationResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setError("");
      void apiPost<BuildResult>("/api/regex/build", { regex, textbook }).then(setBuild).catch((reason: unknown) => {
        setBuild(null);
        setError(reason instanceof ApiError ? reason.message : "Could not build regex.");
      });
    }, 350);
    return () => window.clearTimeout(timer);
  }, [regex, textbook]);

  async function simulate() {
    if (!build) return;
    try {
      const result = await apiPost<{ results: SimulationResult[] }>("/api/automata/simulate", {
        automaton: build[selected],
        strings: [testString],
      });
      setVerdict(result.results[0] ?? null);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Could not simulate string.");
    }
  }

  async function exportReport() {
    if (!build) return;
    setBusy(true);
    try {
      await downloadPost("/api/reports/pdf", { title: "RegexForge Studio report", regex, textbook, strings: testString ? [{ value: testString }] : [] }, "regexforge-report.pdf");
      await downloadPost("/api/reports/csv", { kind: "transition_table", automaton: build[selected] }, "transitions.csv");
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Export failed.");
    } finally { setBusy(false); }
  }
  const automaton = build?.[selected];
  return <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-8">
    <div><h1 className="text-3xl font-bold">Regex Studio</h1><p className="text-slate-300">Type a regex to build and compare its automata.</p></div>
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <label className="block text-sm text-slate-300" htmlFor="regex">Regular expression</label>
      <input id="regex" className="mt-2 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-3 font-mono" value={regex} onChange={(event) => setRegex(event.target.value)} />
      <label className="mt-3 flex gap-2 text-sm"><input type="checkbox" checked={textbook} onChange={(event) => setTextbook(event.target.checked)} /> Textbook mode</label>
      {error && <p className="mt-3 text-red-300" role="alert">{error}</p>}
      {build && <div className="mt-3 text-sm text-slate-400"><span>Canonical: <code>{build.canonical}</code> · Alphabet: {build.alphabet.join(", ") || "∅"}</span></div>}
    </section>
    {automaton && <><div className="flex flex-wrap gap-2">{(["nfa", "dfa", "min_dfa"] as const).map((name) =>
      <button className={`rounded-lg px-3 py-2 text-sm ${selected === name ? "bg-cyan-400 text-slate-950" : "bg-slate-800"}`} key={name} onClick={() => setSelected(name)}>{name === "min_dfa" ? "Min DFA" : name.toUpperCase()}</button>)}</div>
      <AutomatonGraph automaton={automaton} />
      <section className="overflow-auto rounded-xl border border-slate-700 bg-slate-900 p-3"><AutomatonTable table={build.tables[selected]} /></section>
      <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
        <h2 className="mb-3 text-xl font-semibold">Test a string</h2>
        <div className="flex flex-col gap-2 sm:flex-row"><input className="min-w-0 flex-1 rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono" value={testString} onChange={(event) => setTestString(event.target.value)} placeholder="abcb" /><button className="rounded-lg bg-cyan-400 px-4 font-semibold text-slate-950" onClick={() => void simulate()}>Simulate</button><button className="rounded-lg bg-slate-700 px-4" disabled={busy} onClick={() => void exportReport()}>Export PDF + CSV</button></div>
        {verdict && <p className={`mt-3 font-semibold ${verdict.accepted ? "text-emerald-300" : "text-red-300"}`}>{verdict.accepted ? "Accepted" : "Rejected"} — {verdict.reason}</p>}
      </section>
      <StepsPanel steps={build.steps_by_stage[selected] ?? []} />
      <Disclaimer />
    </>}
  </main>;
}
