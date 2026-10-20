import type { TransitionTable } from "@/lib/types";

export function TransitionTable({ table }: { table: TransitionTable }) {
  return (
    <table className="w-full text-left text-sm">
      <thead className="bg-slate-950/60 text-xs uppercase tracking-wide text-slate-400"><tr><th className="p-3">State</th>{table.alphabet.map((symbol) => <th className="p-3" key={symbol}>{symbol}</th>)}</tr></thead>
      <tbody>
        {table.rows.map((row) => (
          <tr className="border-t border-slate-700/70" key={row.state}>
            <td className="p-3 font-mono text-cyan-200">{row.start ? "→ " : ""}{row.accepting ? "★ " : ""}{row.state}</td>
            {table.alphabet.map((symbol) => <td className="p-3 font-mono text-slate-300" key={symbol}>{row.cells[symbol]?.join(", ") || "—"}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
