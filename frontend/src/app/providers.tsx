"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const pathname = usePathname();
  const navigation = [
    ["Home", "/"],
    ["Studio", "/studio"],
    ["Lab", "/lab"],
    ["Grammar", "/grammar"],
    ["Analyzer", "/analyzer"],
    ["Proofs", "/proofs"],
    ["Help", "/help"],
  ] as const;
  return (
    <QueryClientProvider client={queryClient}>
      <header className="sticky top-0 z-40 border-b border-slate-800/70 bg-slate-950/75 px-4 shadow-xl shadow-slate-950/20 backdrop-blur-2xl sm:px-6">
        <nav className="mx-auto flex min-h-[4.5rem] max-w-7xl items-center justify-between gap-5" aria-label="Main navigation">
          <Link className="group flex shrink-0 items-center gap-3 rounded-2xl py-2 pr-2 text-white outline-none focus-visible:ring-2 focus-visible:ring-cyan-300" href="/">
            <Image src="/logo.png" width={40} height={40} alt="" aria-hidden="true" className="size-10 object-contain transition-transform duration-200 group-hover:scale-105" />
            <span className="hidden text-[0.95rem] font-semibold tracking-tight sm:inline">RegexForge</span>
          </Link>
          <div className="flex min-w-0 flex-1 justify-end overflow-x-auto py-1">
            <div className="flex items-center gap-1 rounded-2xl border border-slate-800/80 bg-slate-900/65 p-1 shadow-inner shadow-slate-950/40">
              {navigation.map(([label, href]) => {
                const active = pathname === href;
                return <Link
                  aria-current={active ? "page" : undefined}
                  className={`whitespace-nowrap rounded-xl px-3 py-2 text-xs font-medium outline-none transition-all duration-200 focus-visible:ring-2 focus-visible:ring-cyan-300 sm:px-3.5 sm:text-sm ${active ? "bg-cyan-300 font-semibold text-slate-950 shadow-md shadow-cyan-950/30" : "text-slate-400 hover:bg-slate-800/90 hover:text-cyan-100"}`}
                  href={href}
                  key={href}
                >
                  {label}
                </Link>;
              })}
            </div>
          </div>
        </nav>
      </header>
      {children}
    </QueryClientProvider>
  );
}
