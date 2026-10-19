"use client";

import { useState } from "react";
import type { Step } from "@/lib/types";

export function StepsPanel({ steps }: { steps: Step[] }) {
  const [open, setOpen] = useState(true);
  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900">
      <button className="w-full px-4 py-3 text-left font-semibold" onClick={() => setOpen(!open)}>
        {open ? "Hide" : "Show"} explanation steps ({steps.length})
      </button>
      {open && (
        <div className="space-y-2 border-t border-slate-700 p-3">
          {steps.map((step, index) => (
            <article key={`${step.title}-${index}`} className="rounded-lg bg-slate-800 p-3">
              <h3 className="font-medium text-cyan-200">{step.title}</h3>
              <p className="text-sm text-slate-300">{step.description}</p>
              <pre className="mt-2 overflow-auto text-xs text-slate-400">{JSON.stringify(step.data, null, 2)}</pre>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
