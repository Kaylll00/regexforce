"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AutomatonGraph } from "@/components/AutomatonGraph";
import { RuleEditor } from "@/components/RuleEditor";
import { StepsPanel } from "@/components/StepsPanel";
import { TransitionTable } from "@/components/TransitionTable";
import { ApiError, apiPost } from "@/lib/api";
import { relationClass, relationLabel, type Relation } from "@/lib/analyzerHelpers";
import type { Automaton, Rule, SimulationResult, Step, TransitionTable as TransitionTableData } from "@/lib/types";

type Comparison = { equivalent: boolean; counterexample: string | null; a_accepts: boolean; b_accepts: boolean; steps: Step[] };
type OperationResult = { automaton: Automaton; table: TransitionTableData; steps: Step[] };
type Properties = { empty: boolean; finite: boolean; universal: boolean; shortest_accepted: string | null };
type MatrixCell = { rule: string; relation: Relation; witnesses: Record<string, string | null> };

const defaultRule: Rule = { kind: "regex", regex: "(a|b)*abb" };

export default function AnalyzerPage() {
  const router = useRouter();
  const [tab, setTab] = useState("compare");
  const [first, setFirst] = useState<Rule>(defaultRule);
  const [second, setSecond] = useState<Rule>({ kind: "regex", regex: "(a|b)*ab" });
  const [compare, setCompare] = useState<Comparison | null>(null);
  const [operation, setOperation] = useState("union");
  const [operationResult, setOperationResult] = useState<OperationResult | null>(null);
  const [properties, setProperties] = useState<Properties | null>(null);
  const [rules, setRules] = useState([{ name: "Rule 1", rule: defaultRule }, { name: "Rule 2", rule: second }]);
  const [matrix, setMatrix] = useState<MatrixCell[][] | null>(null);
  const [redundant, setRedundant] = useState<string[]>([]);
  const [testString, setTestString] = useState("");
  const [simulations, setSimulations] = useState<SimulationResult[]>([]);
  const [error, setError] = useState("");

  async function request<T>(path: string, body: unknown): Promise<T | null> {
    try { setError(""); return await apiPost<T>(path, body); }
    catch (reason) { setError(reason instanceof ApiError ? reason.message : "Analyzer request failed."); return null; }
  }
  async function runCompare() {
    const result = await request<Comparison>("/api/analysis/equivalence", { a: first, b: second });
    if (result) setCompare(result);
  }
  async function runOperation() {
    const result = await request<OperationResult>("/api/analysis/closure", { operation, operands: operation === "complement" || operation === "star" || operation === "reversal" ? [first] : [first, second], minimize: true });
    if (result) setOperationResult(result);
  }
  async function runProperties() {
    const result = await request<Properties>("/api/analysis/properties", { rule: first });
    if (result) setProperties(result);
  }
  async function compareAll() {
    const result = await request<{ matrix: MatrixCell[][]; redundant: string[] }>("/api/analysis/compare-many", { rules });
    if (result) { setMatrix(result.matrix); setRedundant(result.redundant); }
  }
  async function simulateRule(rule: Rule) {
    const built = await request<{ min_dfa: Automaton }>("/api/regex/build", { regex: rule.regex ?? "" });
    if (!built) return;
    const result = await request<{ results: SimulationResult[] }>("/api/automata/simulate", { automaton: built.min_dfa, strings: [testString] });
    if (result) setSimulations((current) => [...current, ...result.results]);
  }
  function sendToLab() {
    if (operationResult) sessionStorage.setItem("regexforge-lab-automaton", JSON.stringify(operationResult.automaton));
    router.push("/lab");
  }
  async function saveRule(rule: Rule, name: string) {
    const projectId = sessionStorage.getItem("regexforge-project-id");
    if (!projectId) { setError("Select a project before saving."); return; }
    const result = await request(`/api/projects/${projectId}/rules`, { name, kind: rule.kind, definition: rule });
    if (result) setError(`${name} saved.`);
  }
  return <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-8">
    <div><h1 className="text-3xl font-bold">Language Analyzer</h1><p className="text-slate-300">Compare languages, apply closure operations, inspect properties, and review rule sets.</p></div>
    <nav className="flex flex-wrap gap-2">{["compare", "operations", "properties", "rules"].map((item) => <button className={`rounded px-3 py-2 ${tab === item ? "bg-cyan-400 text-slate-950" : "bg-slate-800"}`} key={item} onClick={() => setTab(item)}>{item}</button>)}</nav>
    {error && <p className="rounded border border-red-800 bg-red-950/40 p-3 text-red-200" role="alert">{error}</p>}
    {tab === "compare" && <section className="space-y-4"><div className="grid gap-4 lg:grid-cols-2"><div><RuleEditor label="Rule A" value={first} onChange={setFirst} /><button className="mt-2 rounded bg-slate-700 px-3 py-1" onClick={() => void saveRule(first, "Analyzer rule A")}>Save rule A</button></div><div><RuleEditor label="Rule B" value={second} onChange={setSecond} /><button className="mt-2 rounded bg-slate-700 px-3 py-1" onClick={() => void saveRule(second, "Analyzer rule B")}>Save rule B</button></div></div><button className="rounded bg-cyan-700 px-4 py-2" onClick={() => void runCompare()}>Check equivalence</button>{compare && <section className={`rounded-xl p-4 ${compare.equivalent ? "bg-emerald-900" : "bg-red-900"}`}><h2 className="font-semibold">{compare.equivalent ? "Equivalent" : "Not equivalent"}</h2>{!compare.equivalent && <p className="mt-2">Counterexample: <code>{compare.counterexample || "ε"}</code>. Rule A {compare.a_accepts ? "accepts" : "rejects"} it; Rule B {compare.b_accepts ? "accepts" : "rejects"} it.</p>}<StepsPanel steps={compare.steps} /></section>}</section>}
    {tab === "operations" && <section className="space-y-4"><div className="grid gap-4 lg:grid-cols-2"><RuleEditor label="Operand A" value={first} onChange={setFirst} /><RuleEditor label="Operand B" value={second} onChange={setSecond} /></div><div className="flex flex-wrap gap-2"><select className="rounded bg-slate-800 p-2" value={operation} onChange={(event) => setOperation(event.target.value)}>{["union", "intersection", "difference", "symmetric_difference", "complement", "concatenation", "star", "reversal"].map((item) => <option key={item}>{item}</option>)}</select><button className="rounded bg-cyan-700 px-3 py-2" onClick={() => void runOperation()}>Apply operation</button></div>{operationResult && <section className="space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-4"><AutomatonGraph automaton={operationResult.automaton} /><TransitionTable table={operationResult.table} /><button className="rounded bg-slate-700 px-3 py-2" onClick={() => void navigator.clipboard.writeText(JSON.stringify(operationResult.automaton, null, 2))}>Copy automaton JSON</button><button className="ml-2 rounded bg-slate-700 px-3 py-2" onClick={sendToLab}>Send to Lab</button><StepsPanel steps={operationResult.steps} /></section>}</section>}
    {tab === "properties" && <section className="space-y-4"><RuleEditor value={first} onChange={setFirst} /><button className="rounded bg-cyan-700 px-3 py-2" onClick={() => void runProperties()}>Check properties</button>{properties && <div className="grid gap-3 sm:grid-cols-4 rounded-xl bg-slate-900 p-4"><span>Empty: {String(properties.empty)}</span><span>Finite: {String(properties.finite)}</span><span>Universal: {String(properties.universal)}</span><span>Shortest: {properties.shortest_accepted || "ε / none"}</span></div>}</section>}
    {tab === "rules" && <section className="space-y-4"><div className="space-y-3">{rules.map((item, index) => <div className="rounded-xl border border-slate-700 p-3" key={item.name}><input className="mb-2 rounded bg-slate-950 p-2" value={item.name} onChange={(event) => setRules(rules.map((rule, itemIndex) => itemIndex === index ? { ...rule, name: event.target.value } : rule))} /><RuleEditor value={item.rule} onChange={(rule) => setRules(rules.map((entry, itemIndex) => itemIndex === index ? { ...entry, rule } : entry))} /></div>)}</div><button className="rounded bg-slate-700 px-3 py-2" onClick={() => setRules([...rules, { name: `Rule ${rules.length + 1}`, rule: { kind: "regex", regex: "a*" } }])}>Add rule</button><button className="ml-2 rounded bg-cyan-700 px-3 py-2" onClick={() => void compareAll()}>Compare all</button>{matrix && <div className="overflow-auto"><table className="w-full text-sm"><tbody>{matrix.map((row, index) => <tr key={rules[index]?.name}>{row.map((cell) => <td className={`border border-slate-700 p-3 ${relationClass(cell.relation)}`} key={cell.rule} title={JSON.stringify(cell.witnesses)}>{relationLabel(cell.relation)}</td>)}</tr>)}</tbody></table><p className="mt-3">Redundant rules: {redundant.join(", ") || "none"}</p></div>}<div className="rounded-xl border border-slate-700 p-4"><h2 className="font-semibold">Test rule</h2><input className="mt-2 rounded bg-slate-950 p-2 font-mono" value={testString} onChange={(event) => setTestString(event.target.value)} /><button className="ml-2 rounded bg-cyan-700 px-3 py-2" onClick={() => { setSimulations([]); for (const item of rules) void simulateRule(item.rule); }}>Check verdicts</button>{simulations.map((simulation, index) => <p key={`${simulation.string}-${index}`} className={simulation.accepted ? "text-emerald-300" : "text-red-300"}>{simulation.accepted ? "Accepted" : "Rejected"}: {simulation.string || "ε"}</p>)}</div></section>}
  </main>;
}
