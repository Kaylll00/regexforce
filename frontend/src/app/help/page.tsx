import Link from "next/link";

const syntax = [
  ["a", "literal symbol"],
  ["ε", "empty string"],
  ["∅", "empty language"],
  ["rs", "concatenation"],
  ["r|s", "union"],
  ["r*", "Kleene star"],
  ["(r)", "grouping"],
];

const modules = [
  { name: "Studio", description: "Build regex automata and simulate strings.", href: "/studio", number: "01" },
  { name: "Lab", description: "Edit and convert automata.", href: "/lab", number: "02" },
  { name: "Grammar", description: "Convert regular grammars and inspect derivations.", href: "/grammar", number: "03" },
  { name: "Analyzer", description: "Compare languages and apply closure operations.", href: "/analyzer", number: "04" },
  { name: "Proofs", description: "Perform guided Pumping Lemma demonstrations.", href: "/proofs", number: "05" },
];

export default function HelpPage() {
  return <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-8 px-6 py-10 sm:py-12">
    <header className="py-2">
      <p className="eyebrow">Quick reference</p>
      <h1 className="mt-3 text-3xl font-bold text-white sm:text-4xl">RegexForge Help</h1>
      <p className="mt-2 max-w-2xl text-slate-300">A guide to the supported classical-language tools.</p>
    </header>

    <section aria-labelledby="syntax-heading" className="surface rounded-2xl p-5 sm:p-6">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
        <div><p className="eyebrow">Reference</p><h2 id="syntax-heading" className="mt-1 text-xl font-semibold text-white">Supported syntax</h2></div>
        <p className="text-sm text-slate-400">Core regular expression notation</p>
      </div>
      <dl className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {syntax.map(([token, meaning]) => <div key={token} className="flex min-h-16 items-center gap-3 rounded-xl border border-slate-700/80 bg-slate-950/45 px-4 py-3">
          <dt className="grid min-w-14 place-items-center rounded-lg border border-cyan-300/15 bg-cyan-300/10 px-2 py-1.5 font-mono font-semibold text-cyan-200">{token}</dt>
          <dd className="text-sm text-slate-300">{meaning}</dd>
        </div>)}
      </dl>
    </section>

    <section aria-labelledby="modules-heading" className="surface rounded-2xl p-5 sm:p-6">
      <div className="mb-4"><p className="eyebrow">Explore</p><h2 id="modules-heading" className="mt-1 text-xl font-semibold text-white">Modules</h2></div>
      <div className="grid items-start gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {modules.map((module) => <Link key={module.name} href={module.href} className="surface group grid min-h-28 grid-cols-[2.5rem_minmax(0,1fr)_1.5rem] grid-rows-[auto_auto] items-start gap-x-3 gap-y-2 self-start rounded-2xl p-3 sm:p-4 hover:border-cyan-400/60">
          <div className="contents"><span className="row-span-2 grid size-9 place-items-center rounded-lg border border-cyan-300/15 bg-cyan-300/10 font-mono text-xs font-semibold text-cyan-200">{module.number}</span><span aria-hidden="true" className="col-start-3 row-start-1 justify-self-end self-center text-slate-500 transition-transform group-hover:translate-x-1 group-hover:text-cyan-200">→</span></div>
          <h3 className="col-start-2 row-start-1 min-w-0 self-center font-semibold text-white">{module.name}</h3>
          <p className="col-start-2 col-end-4 row-start-2 text-sm leading-5 text-slate-400">{module.description}</p>
        </Link>)}
      </div>
    </section>
  </main>;
}
