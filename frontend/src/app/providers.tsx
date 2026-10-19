"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={queryClient}>
      <header className="border-b border-slate-800 bg-slate-950">
        <nav className="mx-auto flex max-w-7xl flex-wrap gap-4 px-6 py-4 text-sm">
          {[
            ["Home", "/"], ["Studio", "/studio"], ["Lab", "/lab"], ["Grammar", "/grammar"],
            ["Analyzer", "/analyzer"], ["Proofs", "/proofs"], ["Help", "/help"],
          ].map(([label, href]) => <Link className="text-slate-300 hover:text-cyan-200" href={href} key={href}>{label}</Link>)}
        </nav>
      </header>
      {children}
    </QueryClientProvider>
  );
}
