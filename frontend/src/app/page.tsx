import Link from "next/link";

export default function Home() {
  return <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-6 py-16">
    <p className="text-sm uppercase tracking-widest text-cyan-300">RegexForge</p>
    <h1 className="max-w-3xl text-5xl font-bold">Explore regular languages with proof-friendly explanations.</h1>
    <p className="max-w-2xl text-lg text-slate-300">Build automata from classical regexes, inspect every transformation, and test strings interactively.</p>
    <Link className="w-fit rounded-lg bg-cyan-400 px-5 py-3 font-semibold text-slate-950" href="/studio">Open Regex Studio</Link>
  </main>;
}
