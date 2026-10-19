"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={queryClient}>
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/85 shadow-lg shadow-slate-950/20 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl flex-wrap items-center gap-2 px-6 py-3 text-sm">
          <Link className="mr-3 flex items-center gap-2 rounded-xl px-2 py-2 font-semibold text-white" href="/"><span className="grid h-7 w-7 place-items-center rounded-lg bg-cyan-300 font-mono text-sm text-slate-950">R</span>RegexForge</Link>
          {[
            ["Home", "/"], ["Studio", "/studio"], ["Lab", "/lab"], ["Grammar", "/grammar"],
            ["Analyzer", "/analyzer"], ["Proofs", "/proofs"], ["Help", "/help"],
          ].map(([label, href]) => <Link className="rounded-lg px-3 py-2 text-slate-400 outline-none hover:bg-slate-800 hover:text-cyan-200 focus:ring-2 focus:ring-cyan-300" href={href} key={href}>{label}</Link>)}
        </nav>
      </header>
      {children}
    </QueryClientProvider>
  );
}
