"use client";

import { useEffect, useState } from "react";
import { AutomatonGraph } from "@/components/AutomatonGraph";
import { Disclaimer } from "@/components/Disclaimer";
import { StepsPanel } from "@/components/StepsPanel";
import { TransitionTable } from "@/components/TransitionTable";
import { apiPost, ApiError } from "@/lib/api";
import { addState, addTransition, removeState, renameState, setStart, setType, toggleAccepting } from "@/lib/automatonEdit";
import { exampleAutomaton, useLabStore } from "@/lib/labStore";
import type { Automaton, SimulationResult, Step, TransitionTable as TransitionTableData } from "@/lib/types";
import type { Connection } from "@xyflow/react";

type ActionResult = { automaton: Automaton; table: TransitionTableData; steps: Step[] };
type RegexResult = { regex: string; steps: Step[] };

export default function Lab() {
  const { automaton, selectedState, result, dirty, setAutomaton, selectState, setResult, markExported } = useLabStore();
  const [error, setError] = useState("");
  const [trimDead, setTrimDead] = useState(false);
  const [method, setMethod] = useState<"state_elimination" | "arden">("state_elimination");
  const [importText, setImportText] = useState("");
  const [testString, setTestString] = useState("");
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);

  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (dirty) { event.preventDefault(); event.returnValue = ""; }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);

  function edit(update: Automaton) { setAutomaton(update); setError(""); }
  function connect(connection: Connection) {
    if (!connection.source || !connection.target) return;
    const symbol = window.prompt("Transition symbol (use ε for epsilon):", "a");
    if (symbol) edit(addTransition(automaton, connection.source, connection.target, symbol));
  }
  async function action(path: string, body: Record<string, unknown>, regex = false) {
    try {
      setError("");
      const response = await apiPost<ActionResult | RegexResult>(path, body);
      if (regex) setResult(response as RegexResult);
      else setResult(response as ActionResult);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "The operation failed.");
    }
  }
  function exportAutomaton() {
    const blob = new Blob([JSON.stringify(automaton, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url; link.download = "automaton.json"; link.click(); URL.revokeObjectURL(url);
    markExported();
  }
  async function importAutomaton() {
    try {
      const parsed = JSON.parse(importText) as Automaton;
      const validated = await apiPost<{ automaton: Automaton }>("/api/automata/validate", { automaton: parsed });
      edit(validated.automaton);
      setImportText("");
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Invalid automaton JSON.");
    }
  }
  async function simulate() {
    try {
      const response = await apiPost<{ results: SimulationResult[] }>("/api/automata/simulate", { automaton, strings: [testString] });
      setSimulation(response.results[0] ?? null);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Simulation failed.");
    }
  }
  const selected = selectedState ? automaton.states.find((state) => state === selectedState) : undefined;
  const regexResult = result && "regex" in result ? result as { regex: string; steps: Step[] } : undefined;
  const actionResult = result && "automaton" in result ? result as ActionResult : undefined;
  const resultAutomaton = actionResult?.automaton;

  return <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-8">
    <div><h1 className="text-3xl font-bold">Automata Lab</h1><p className="text-slate-300">Build, edit, convert, and export finite automata.</p></div>
    <section className="grid grid-cols-2 items-stretch gap-2 rounded-xl border border-slate-700 bg-slate-900 p-4 sm:flex sm:flex-wrap sm:items-center">
      <button className="min-h-16 w-full rounded bg-slate-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={() => edit(addState(automaton, `q${automaton.states.length}`))}>Add state</button>
      <button className="min-h-16 w-full rounded bg-slate-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={() => edit(exampleAutomaton)}>Load example</button>
      <button className="min-h-16 w-full rounded bg-slate-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={exportAutomaton}>Export JSON</button>
      <select className="min-h-16 w-full rounded bg-slate-800 px-3 py-2 text-center sm:min-h-10 sm:w-auto" value={automaton.type} onChange={(event) => edit(setType(automaton, event.target.value as "nfa" | "dfa"))}><option value="nfa">NFA</option><option value="dfa">DFA</option></select>
      <label className="col-span-2 flex min-h-11 items-center justify-center gap-2 text-sm sm:col-span-1 sm:ml-auto"><input type="checkbox" checked={trimDead} onChange={(event) => setTrimDead(event.target.checked)} /> Trim dead state</label>
    </section>
    <section className="grid min-w-0 gap-4 lg:grid-cols-[minmax(0,1fr)_17rem] lg:gap-6">
      <AutomatonGraph automaton={automaton} editable onSelectState={selectState} onConnect={connect} height={420} />
      <aside className="rounded-xl border border-slate-700 bg-slate-900 p-4">
        <h2 className="font-semibold">Selected state</h2>
        {selected ? <div className="mt-3 space-y-3">
          <p className="font-mono">{selected}</p>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap">
            <button className="min-h-16 w-full rounded bg-slate-700 px-3 py-2 text-sm sm:min-h-10 sm:w-auto" onClick={() => edit(setStart(automaton, selected))}>Set start</button>
            <button className="min-h-16 w-full rounded bg-slate-700 px-3 py-2 text-sm sm:min-h-10 sm:w-auto" onClick={() => edit(toggleAccepting(automaton, selected))}>Toggle accepting</button>
            <button className="min-h-16 w-full rounded bg-slate-700 px-3 py-2 text-sm sm:min-h-10 sm:w-auto" onClick={() => { const next = window.prompt("New state name:", selected); if (next) edit(renameState(automaton, selected, next)); }}>Rename</button>
            <button className="min-h-16 w-full rounded bg-red-900 px-3 py-2 text-sm sm:min-h-10 sm:w-auto" onClick={() => edit(removeState(automaton, selected))}>Delete state</button>
          </div>
        </div> : <p className="mt-3 text-sm text-slate-400">Select a state in the graph.</p>}
      </aside>
    </section>
    {automaton.type === "dfa" && <p className="rounded border border-amber-700 bg-amber-950/40 p-3 text-sm">DFA checks are enforced before conversion: {checkDfa(automaton).join(" ") || "no determinism problems detected."}</p>}
    <section className="grid grid-cols-2 gap-2 rounded-xl border border-slate-700 bg-slate-900 p-4 sm:flex sm:flex-wrap">
      <button className="min-h-16 w-full rounded bg-cyan-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={() => void action("/api/automata/validate", { automaton })}>Validate</button>
      <button className="min-h-16 w-full rounded bg-cyan-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={() => void action("/api/automata/to-dfa", { automaton })}>NFA → DFA</button>
      <button className="min-h-16 w-full rounded bg-cyan-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={() => void action("/api/automata/complete", { automaton })}>Complete DFA</button>
      <button className="min-h-16 w-full rounded bg-cyan-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={() => void action("/api/automata/minimize", { automaton, trim_dead: trimDead })}>Minimize</button>
      <select className="min-h-16 w-full rounded bg-slate-800 px-3 text-center sm:min-h-10 sm:w-auto" value={method} onChange={(event) => setMethod(event.target.value as typeof method)}><option value="state_elimination">State elimination</option><option value="arden">Arden</option></select>
      <button className="min-h-16 w-full rounded bg-cyan-700 px-3 py-2 text-center sm:min-h-10 sm:w-auto" onClick={() => void action("/api/automata/to-regex", { automaton, method })}>To regex</button>
    </section>
    {error && <p className="text-red-300" role="alert">{error}</p>}
    {regexResult && <section className="rounded-xl border border-cyan-700 bg-slate-900 p-4"><h2 className="font-semibold">Regex result</h2><code className="mt-2 block rounded bg-slate-950 p-3">{regexResult.regex}</code><button className="mt-3 rounded bg-slate-700 px-3 py-2" onClick={() => void navigator.clipboard.writeText(regexResult.regex)}>Copy regex</button><a className="ml-2 rounded bg-slate-700 px-3 py-2" href={`/studio?regex=${encodeURIComponent(regexResult.regex)}`}>Open in Studio</a><StepsPanel steps={regexResult.steps} /></section>}
    {resultAutomaton && actionResult && <section className="space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-4"><h2 className="text-xl font-semibold">Conversion result</h2><AutomatonGraph automaton={resultAutomaton} /><TransitionTable table={actionResult.table} /><StepsPanel steps={actionResult.steps} /><button className="rounded bg-cyan-700 px-3 py-2" onClick={() => edit(resultAutomaton)}>Use result as current automaton</button></section>}
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4"><h2 className="font-semibold">Import JSON</h2><textarea className="mt-2 min-h-24 w-full rounded bg-slate-950 p-3 font-mono text-sm" value={importText} onChange={(event) => setImportText(event.target.value)} placeholder="Paste automaton JSON here" /><button className="w-full rounded bg-slate-700 px-3 py-2 sm:w-auto" onClick={() => void importAutomaton()}>Validate and import</button></section>
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4"><h2 className="font-semibold">Test string</h2><div className="mt-2 flex flex-col gap-2 sm:flex-row"><input className="min-w-0 flex-1 rounded bg-slate-950 p-2 font-mono" value={testString} onChange={(event) => setTestString(event.target.value)} /><button className="rounded bg-cyan-700 px-3" onClick={() => void simulate()}>Simulate</button></div>{simulation && <p className={`mt-3 font-semibold ${simulation.accepted ? "text-emerald-300" : "text-red-300"}`}>{simulation.accepted ? "Accepted" : "Rejected"} — {simulation.reason}</p>}{simulation && <StepsPanel steps={simulation.steps.map((step) => ({ title: `Step ${step.index}`, description: step.note, data: step as unknown as Record<string, unknown>, kind: "info" }))} />}</section>
    <Disclaimer />
  </main>;
}

function checkDfa(automaton: Automaton): string[] {
  const seen = new Set<string>();
  const problems: string[] = [];
  for (const transition of automaton.transitions) {
    const key = `${transition.from}:${transition.symbol}`;
    if (transition.symbol === "ε") problems.push(`ε transition from ${transition.from}.`);
    if (seen.has(key)) problems.push(`duplicate transition ${key}.`);
    seen.add(key);
  }
  return problems;
}
