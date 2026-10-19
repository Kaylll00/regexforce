"use client";

import { useEffect, useState } from "react";
import { AutomatonGraph } from "@/components/AutomatonGraph";
import { DerivationViewer } from "@/components/DerivationViewer";
import { StepsPanel } from "@/components/StepsPanel";
import { TransitionTable } from "@/components/TransitionTable";
import { ApiError, apiPost } from "@/lib/api";
import { grammarExamples } from "@/lib/grammarExamples";
import type { Automaton, Step, TransitionTable as TransitionTableData } from "@/lib/types";

type ParseResult = {
  kind: string;
  productions: Array<{ head: string; body: string[] }>;
  canonical: string;
  steps: Step[];
};
type AutomatonResult = {
  nfa: Automaton;
  dfa: Automaton;
  tables: { nfa: TransitionTableData; dfa: TransitionTableData };
  steps: Step[];
};
type RegexResult = { regex: string; steps: Step[] };
type DerivationResult = { accepted: boolean; forms: string[] | null; steps: Step[] };

export default function GrammarPage() {
  const [grammar, setGrammar] = useState<string>(grammarExamples["Right-linear"]);
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [conversion, setConversion] = useState<AutomatonResult | null>(null);
  const [regexResult, setRegexResult] = useState<RegexResult | null>(null);
  const [fromRegex, setFromRegex] = useState("");
  const [convertedGrammar, setConvertedGrammar] = useState("");
  const [fromAutomaton, setFromAutomaton] = useState("");
  const [derivedString, setDerivedString] = useState("");
  const [derivation, setDerivation] = useState<DerivationResult | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setError(null);
      void apiPost<ParseResult>("/api/grammar/parse", { grammar })
        .then(setParseResult)
        .catch((reason: unknown) => {
          setParseResult(null);
          setError(toApiError(reason));
        });
    }, 350);
    return () => window.clearTimeout(timer);
  }, [grammar]);

  async function run<T>(path: string, body: unknown, callback: (value: T) => void) {
    setLoading(true);
    setError(null);
    try {
      callback(await apiPost<T>(path, body));
    } catch (reason) {
      setError(toApiError(reason));
    } finally {
      setLoading(false);
    }
  }

  async function copy(value: string) {
    await navigator.clipboard.writeText(value);
  }

  function convertAutomatonToGrammar() {
    try {
      const automaton = JSON.parse(fromAutomaton) as Automaton;
      void run<{ grammar: string; steps: Step[] }>("/api/grammar/from-automaton", { automaton }, (result) => setFromAutomaton(result.grammar));
    } catch {
      setError(new ApiError("Automaton input is not valid JSON.", "automaton_invalid"));
    }
  }

  const normalized = parseResult?.productions
    .map((production) => `${production.head} -> ${production.body.join("")}`)
    .join("\n");
  return (
    <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-8">
      <div>
        <h1 className="text-3xl font-bold">Grammar Converter</h1>
        <p className="text-slate-300">Parse regular grammars, inspect their derivations, and convert them to automata or regex.</p>
      </div>
      <section className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <label className="block text-sm text-slate-300" htmlFor="grammar-input">Grammar</label>
          <textarea id="grammar-input" className="mt-2 min-h-48 w-full rounded-lg bg-slate-950 p-3 font-mono text-sm" value={grammar} onChange={(event) => setGrammar(event.target.value)} />
          <p className="mt-3 text-xs text-slate-400">Use single uppercase ASCII nonterminals, one production per line, and single-character terminals. Epsilon is ε or \e.</p>
          {error && <p className="mt-3 rounded border border-red-800 bg-red-950/40 p-3 text-red-200" role="alert">{error.code}: {error.message}{error.position ? ` (line ${error.position})` : ""}</p>}
          {parseResult && <div className="mt-4 grid gap-3 sm:grid-cols-2"><p><span className="text-slate-400">Detected kind:</span> {parseResult.kind}</p><pre className="rounded bg-slate-950 p-3 text-sm">{normalized}</pre></div>}
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <label className="block text-sm text-slate-300" htmlFor="grammar-example">Examples</label>
          <select id="grammar-example" className="mt-2 w-full rounded bg-slate-800 p-2" defaultValue="" onChange={(event) => { if (event.target.value) setGrammar(event.target.value); }}>
            <option value="">Choose an example</option>
            {Object.keys(grammarExamples).map((name) => <option key={name} value={grammarExamples[name as keyof typeof grammarExamples]}>{name}</option>)}
          </select>
          <p className="mt-4 text-sm text-slate-400">Regular grammars use uppercase ASCII nonterminals and single-character terminals. Mixed left/right-linear productions are rejected.</p>
        </div>
      </section>
      <section className="flex flex-wrap gap-2 rounded-xl border border-slate-700 bg-slate-900 p-4">
        <button className="rounded bg-cyan-700 px-3 py-2" disabled={loading} onClick={() => void run<AutomatonResult>("/api/grammar/to-automaton", { grammar }, setConversion)}>Grammar → automaton</button>
        <button className="rounded bg-cyan-700 px-3 py-2" disabled={loading} onClick={() => void run<RegexResult>("/api/grammar/to-regex", { grammar }, setRegexResult)}>Grammar → regex</button>
      </section>
      {conversion && <section className="space-y-4 rounded-xl border border-slate-700 bg-slate-900 p-4">
        <h2 className="text-xl font-semibold">Automaton conversion</h2>
        <div className="grid gap-4 lg:grid-cols-2"><div><h3 className="mb-2 font-semibold">NFA</h3><AutomatonGraph automaton={conversion.nfa} /><TransitionTable table={conversion.tables.nfa} /></div><div><h3 className="mb-2 font-semibold">DFA</h3><AutomatonGraph automaton={conversion.dfa} /><TransitionTable table={conversion.tables.dfa} /></div></div>
        <StepsPanel steps={conversion.steps} />
      </section>}
      {regexResult && <section className="rounded-xl border border-cyan-700 bg-slate-900 p-4"><h2 className="font-semibold">Regex result</h2><code className="mt-2 block rounded bg-slate-950 p-3">{regexResult.regex}</code><button className="mt-3 rounded bg-slate-700 px-3 py-2" onClick={() => void copy(regexResult.regex)}>Copy regex</button><StepsPanel steps={regexResult.steps} /></section>}
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4"><h2 className="font-semibold">Regex → grammar</h2><input className="mt-3 w-full rounded bg-slate-950 p-2 font-mono" value={fromRegex} onChange={(event) => setFromRegex(event.target.value)} placeholder="(a|b)*abb" /><button className="mt-3 rounded bg-cyan-700 px-3 py-2" onClick={() => void run<{ grammar: string; steps: Step[] }>("/api/grammar/from-regex", { regex: fromRegex }, (result) => setConvertedGrammar(result.grammar))}>Convert</button>{convertedGrammar && <pre className="mt-3 whitespace-pre-wrap rounded bg-slate-950 p-3 text-sm">{convertedGrammar}</pre>}</div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4"><h2 className="font-semibold">Automaton → grammar</h2><textarea className="mt-3 min-h-28 w-full rounded bg-slate-950 p-2 font-mono text-sm" value={fromAutomaton} onChange={(event) => setFromAutomaton(event.target.value)} placeholder="Paste automaton JSON" /><button className="mt-3 rounded bg-cyan-700 px-3 py-2" onClick={convertAutomatonToGrammar}>Convert</button></div>
      </section>
      <section className="rounded-xl border border-slate-700 bg-slate-900 p-4"><h2 className="font-semibold">Derivation viewer</h2><div className="mt-3 flex gap-2"><input className="flex-1 rounded bg-slate-950 p-2 font-mono" value={derivedString} onChange={(event) => setDerivedString(event.target.value)} placeholder="String to derive" /><button className="rounded bg-cyan-700 px-3 py-2" onClick={() => void run<DerivationResult>("/api/grammar/derive", { grammar, string: derivedString }, setDerivation)}>Derive</button></div>{derivation && <div className="mt-4"><DerivationViewer accepted={derivation.accepted} forms={derivation.forms} steps={derivation.steps} /></div>}</section>
    </main>
  );
}

function toApiError(reason: unknown): ApiError {
  return reason instanceof ApiError ? reason : new ApiError("The grammar request failed.", "grammar_error");
}
