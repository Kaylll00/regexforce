"use client";

import { useEffect, useState } from "react";
import { Disclaimer } from "@/components/Disclaimer";
import { StepsPanel } from "@/components/StepsPanel";
import { ApiError, apiPost } from "@/lib/api";
import type { Step } from "@/lib/types";

type Template = { id: string; name: string; description: string; is_regular: boolean; alphabet: string[]; outline: Step[] };
type Decomposition = { x: string; y: string; z: string; x_len: number; y_len: number };
type Check = { pumped: string; in_language: boolean; i: number; decomposition: Decomposition; steps: Step[] };
type Report = { total: number; refuted: number; survivors: Decomposition[]; steps: Step[]; disclaimer: string };

export default function ProofsPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [templateId, setTemplateId] = useState("anbn");
  const [p, setP] = useState(3);
  const [recommended, setRecommended] = useState("");
  const [custom, setCustom] = useState("");
  const [decompositions, setDecompositions] = useState<Decomposition[]>([]);
  const [checks, setChecks] = useState<Record<string, Check>>({});
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");
  const template = templates.find((item) => item.id === templateId);
  const string = custom || recommended;

  useEffect(() => {
    void fetch(`${process.env.NEXT_PUBLIC_API_URL ?? ""}/api/proofs/templates`)
      .then((response) => response.json() as Promise<Template[]>).then(setTemplates)
      .catch(() => setError("Could not load proof templates."));
  }, []);
  useEffect(() => {
    void apiPost<{ string: string }>("/api/proofs/pumping/witness", { template_id: templateId, p })
      .then((result) => { setRecommended(result.string); setCustom(""); setReport(null); setChecks({}); })
      .catch((reason: unknown) => setError(reason instanceof ApiError ? reason.message : "Could not create witness."));
  }, [templateId, p]);
  async function loadDecompositions() {
    try {
      const result = await apiPost<{ problems: string[]; decompositions: Decomposition[] }>("/api/proofs/pumping/decompositions", { template_id: templateId, p, s: string });
      setDecompositions(result.decompositions);
      setError(result.problems.join(" "));
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : "Could not enumerate decompositions."); }
  }
  async function check(item: Decomposition, i = 0) {
    try {
      const result = await apiPost<Check>("/api/proofs/pumping/check", { template_id: templateId, p, s: string, x_len: item.x_len, y_len: item.y_len, i });
      setChecks((current) => ({ ...current, [`${item.x_len}:${item.y_len}`]: result }));
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : "Could not check decomposition."); }
  }
  async function checkAll() {
    try { setReport(await apiPost<Report>("/api/proofs/pumping/check", { template_id: templateId, p, s: string })); }
    catch (reason) { setError(reason instanceof ApiError ? reason.message : "Could not run pumping check."); }
  }
  return <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-8">
    <div><h1 className="text-3xl font-bold">Proof Workbench</h1><p className="text-slate-300">Guided Pumping Lemma demonstrations with a symbolic outline and numeric checker.</p></div>
    <Disclaimer />
    <section className="grid min-w-0 gap-4 rounded-xl border border-slate-700 bg-slate-900 p-4 sm:grid-cols-2 lg:grid-cols-3">
      <label>Template<select className="mt-2 block w-full rounded bg-slate-800 p-2" value={templateId} onChange={(event) => setTemplateId(event.target.value)}>{templates.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
      <label>p = {p}<input className="mt-3 block w-full" type="range" min="1" max="12" value={p} onChange={(event) => setP(Number(event.target.value))} /></label>
      <div><p className="text-sm text-slate-400">Recommended string</p><code className="mt-2 block rounded bg-slate-950 p-2">{recommended || "Loading..."}</code></div>
      <label className="sm:col-span-2 lg:col-span-3">Custom string<input className="mt-2 w-full rounded bg-slate-950 p-2 font-mono" value={custom} onChange={(event) => setCustom(event.target.value)} placeholder="Leave blank to use the recommended witness" /></label>
      {template && <p className="text-sm text-slate-400 sm:col-span-2 lg:col-span-3">{template.description} Alphabet: {template.alphabet.join(", ")}.</p>}
      {error && <p className="text-red-300 sm:col-span-2 lg:col-span-3" role="alert">{error}</p>}
    </section>
    <section className="grid min-w-0 items-start gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <div className="min-w-0 rounded-xl border border-slate-700 bg-slate-900 p-4"><div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap"><button className="w-full rounded bg-slate-700 px-3 py-2 sm:w-auto" onClick={() => void loadDecompositions()}>Load decompositions</button><button className="w-full rounded bg-cyan-700 px-3 py-2 sm:w-auto" onClick={() => void checkAll()}>Check all</button></div>{decompositions.length > 0 && <div className="mt-4 hidden w-full max-w-full overflow-x-auto overscroll-x-contain sm:block"><table className="w-full min-w-[560px] table-fixed text-sm"><colgroup><col className="w-[16%]" /><col className="w-[20%]" /><col className="w-[28%]" /><col className="w-[12%]" /><col className="w-[24%]" /></colgroup><thead><tr><th className="p-3 text-center">x</th><th className="p-3 text-center">y</th><th className="p-3 text-center">z</th><th className="p-3 text-center">i</th><th className="p-3 text-center">Result</th></tr></thead><tbody>{decompositions.map((item) => { const result = checks[`${item.x_len}:${item.y_len}`]; return <tr className="border-t border-slate-700" key={`${item.x_len}:${item.y_len}`}><td className="break-all p-3 text-center align-middle font-mono">{item.x || "Îµ"}</td><td className="break-all p-3 text-center align-middle font-mono">{item.y}</td><td className="break-all p-3 text-center align-middle font-mono">{item.z || "Îµ"}</td><td className="p-3 text-center align-middle"><input className="mx-auto block w-16 rounded bg-slate-950 p-2 text-center" type="number" min="0" max="8" defaultValue="0" onChange={(event) => void check(item, Number(event.target.value))} /></td><td className="p-3 text-center align-middle">{result ? result.in_language ? <span className="text-red-300">âˆˆ L âœ—</span> : <span className="text-emerald-300">âˆ‰ L âœ“</span> : <button className="mx-auto text-cyan-300" onClick={() => void check(item)}>Find i</button>}</td></tr>; })}</tbody></table></div>}<div className="space-y-3 sm:hidden">{decompositions.map((item) => { const result = checks[`${item.x_len}:${item.y_len}`]; return <article className="rounded-xl border border-slate-700 bg-slate-950/60 p-3" key={`mobile-${item.x_len}:${item.y_len}`}><dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-sm"><div><dt className="text-xs uppercase tracking-wide text-slate-400">x</dt><dd className="mt-1 break-all font-mono">{item.x || "\u03b5"}</dd></div><div><dt className="text-xs uppercase tracking-wide text-slate-400">y</dt><dd className="mt-1 break-all font-mono">{item.y}</dd></div><div className="col-span-2"><dt className="text-xs uppercase tracking-wide text-slate-400">z</dt><dd className="mt-1 break-all font-mono">{item.z || "\u03b5"}</dd></div></dl><div className="mt-3 grid grid-cols-2 items-end gap-3"><label className="text-xs text-slate-400">Pump count i<input aria-label={`Pump count i for decomposition ${item.x_len}:${item.y_len}`} className="mt-1 block w-full rounded bg-slate-900 p-2 text-center text-sm text-slate-100" type="number" min="0" max="8" defaultValue="0" onChange={(event) => void check(item, Number(event.target.value))} /></label><div className="text-right">{result ? result.in_language ? <span className="text-sm text-red-300">In L</span> : <span className="text-sm text-emerald-300">Not in L</span> : <button className="w-full rounded bg-cyan-700 px-2 py-2 text-sm" onClick={() => void check(item)}>Find i</button>}</div></div></article>; })}</div></div>
      <aside className="rounded-xl border border-slate-700 bg-slate-900 p-4"><h2 className="font-semibold">Valid argument pattern</h2>{template ? <StepsPanel steps={template.outline} /> : <p className="text-slate-400">Loading outline...</p>}</aside>
    </section>
    {report && <section className="rounded-xl border border-cyan-800 bg-slate-900 p-4"><h2 className="text-xl font-semibold">Numeric demonstration for the tested p only</h2><p className="mt-2">Checked {report.total} decompositions; refuted {report.refuted}; survivors {report.survivors.length}.</p><p className="mt-3 text-amber-200">{report.survivors.length ? "This chosen string does not give a contradiction; this proves nothing about regularity." : "For this specific p every decomposition was pumped out of L; a complete proof requires the symbolic argument for arbitrary p."}</p><StepsPanel steps={report.steps} /></section>}
  </main>;
}
