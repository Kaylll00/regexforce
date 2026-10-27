"use client";

import { useState } from "react";
import type { Step } from "@/lib/types";

export function StepsPanel({ steps }: { steps?: Step[] | null }) {
  const safeSteps = Array.isArray(steps) ? steps : [];
  const [open, setOpen] = useState(true);
  return (
    <section className="surface rounded-2xl">
      <button className="w-full px-4 py-4 text-left font-semibold text-slate-100" onClick={() => setOpen(!open)}>
        {open ? "Hide" : "Show"} explanation steps ({safeSteps.length})
      </button>
      {open && (
        <div className="border-t border-slate-700/80 px-4 py-2 sm:px-5">
          {safeSteps.map((step, index) => (
            <article key={`${step.title}-${index}`} className="relative border-l border-slate-700 py-4 pl-7 first:pt-4 last:pb-4">
              <span className="absolute -left-[0.7rem] top-4 grid size-5 place-items-center rounded-full border border-cyan-300/40 bg-slate-900 font-mono text-[10px] font-semibold text-cyan-200">{index + 1}</span>
              <h3 className="font-semibold text-cyan-200">{step.title}</h3>
              <p className="mt-1 text-sm leading-6 text-slate-300">{step.description}</p>
              {Object.keys(step.data ?? {}).length > 0 && <details className="group mt-2">
                <summary className="inline-flex cursor-pointer list-none items-center gap-2 rounded-md px-2 py-1 text-xs font-medium text-slate-400 hover:bg-slate-800 hover:text-cyan-200 [&::-webkit-details-marker]:hidden">
                  <span className="text-cyan-300 group-open:rotate-90">›</span>View step data
                </summary>
                <pre className="mt-2 max-h-48 overflow-auto rounded-lg border border-slate-800 bg-slate-950/80 p-3 text-xs leading-5 text-slate-400">{JSON.stringify(step.data, null, 2)}</pre>
              </details>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
