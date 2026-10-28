"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import Image from "next/image";
import logo from "../../public/logo.png";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  useEffect(() => {
    if (!menuOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [menuOpen]);
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
      <header className="sticky top-0 z-40 border-b border-slate-800/70 bg-slate-950/95 px-3 shadow-xl shadow-slate-950/20 backdrop-blur-2xl sm:px-6">
        <nav className="mx-auto flex min-h-16 max-w-7xl items-center justify-between gap-4" aria-label="Main navigation">
          <Link className="group flex min-w-0 shrink-0 items-center gap-2 rounded-xl py-1 pr-2 text-white outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 sm:gap-3 sm:py-2" href="/">
            <Image src={logo} width={40} height={40} alt="" aria-hidden="true" unoptimized className="size-10 object-contain transition-transform duration-200 group-hover:scale-105" />
            <span className="text-sm font-semibold tracking-tight sm:text-[0.95rem]">RegexForge</span>
          </Link>
          <div className="hidden min-w-0 flex-1 justify-end sm:flex">
            <div className="flex max-w-full items-center gap-1 overflow-x-auto rounded-2xl border border-slate-800/80 bg-slate-900/65 p-1 shadow-inner shadow-slate-950/40 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
              {navigation.map(([label, href]) => {
                const active = pathname === href;
                return <Link
                  aria-current={active ? "page" : undefined}
                  className={`whitespace-nowrap rounded-xl px-3.5 py-2.5 text-sm font-medium outline-none transition-all duration-200 focus-visible:ring-2 focus-visible:ring-cyan-300 ${active ? "bg-cyan-300 font-semibold text-slate-950 shadow-md shadow-cyan-950/30" : "text-slate-400 hover:bg-slate-800/90 hover:text-cyan-100"}`}
                  href={href}
                  key={href}
                >
                  {label}
                </Link>;
              })}
            </div>
          </div>
          <button
            type="button"
            className="grid size-11 shrink-0 place-items-center rounded-xl border border-slate-700 bg-slate-900 text-slate-100 hover:border-cyan-400/70 hover:bg-slate-800 sm:hidden"
            aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={menuOpen}
            aria-controls="mobile-navigation"
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span aria-hidden="true" className="relative block h-4 w-5">
              <span className={`absolute left-0 top-0 h-0.5 w-5 rounded bg-current transition-transform ${menuOpen ? "translate-y-[7px] rotate-45" : ""}`} />
              <span className={`absolute left-0 top-[7px] h-0.5 w-5 rounded bg-current transition-opacity ${menuOpen ? "opacity-0" : "opacity-100"}`} />
              <span className={`absolute left-0 top-[14px] h-0.5 w-5 rounded bg-current transition-transform ${menuOpen ? "-translate-y-[7px] -rotate-45" : ""}`} />
            </span>
          </button>
        </nav>
      </header>
      {menuOpen && <div className="fixed inset-0 z-50 sm:hidden">
        <button className="absolute inset-0 min-h-0 border-0 bg-slate-950/70 shadow-none backdrop-blur-sm" aria-label="Close navigation menu" onClick={() => setMenuOpen(false)} />
        <aside id="mobile-navigation" aria-label="Navigation sidebar" className="absolute inset-y-0 right-0 flex w-[min(21rem,88vw)] flex-col border-l border-slate-700 bg-slate-950 p-5 shadow-2xl shadow-black/50" role="dialog" aria-modal="true">
          <div className="mb-5 flex items-center justify-between border-b border-slate-800 pb-4">
            <div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">RegexForge</p><h2 className="mt-1 text-lg font-semibold text-white">Navigation</h2></div>
            <button type="button" className="grid size-10 place-items-center rounded-xl border border-slate-700 bg-slate-900 text-xl text-slate-200 hover:border-cyan-400/70" aria-label="Close navigation menu" onClick={() => setMenuOpen(false)}>&times;</button>
          </div>
          <nav aria-label="Mobile navigation" className="flex flex-col gap-2">
            {navigation.map(([label, href], index) => {
              const active = pathname === href;
              return <Link
                aria-current={active ? "page" : undefined}
                className={`grid min-h-12 grid-cols-[2rem_minmax(0,1fr)] items-center gap-3 rounded-xl border px-4 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 ${active ? "border-cyan-300/40 bg-cyan-300 text-slate-950" : "border-slate-800 bg-slate-900/80 text-slate-200 hover:border-slate-600 hover:bg-slate-800"}`}
                href={href}
                key={href}
                onClick={() => setMenuOpen(href === "/proofs")}
              ><span className={`text-right font-mono text-xs ${active ? "text-slate-700" : "text-slate-500"}`}>{String(index + 1).padStart(2, "0")}</span><span className="text-left">{label}</span></Link>;
            })}
          </nav>
        </aside>
      </div>}
      {children}
    </QueryClientProvider>
  );
}
