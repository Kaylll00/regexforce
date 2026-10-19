import type { TransitionTable } from "@/lib/types";

export function TransitionTable({ table }: { table: TransitionTable }) {
  return (
    <table className="w-full text-left text-sm">
      <thead><tr><th className="p-2">State</th>{table.alphabet.map((symbol) => <th className="p-2" key={symbol}>{symbol}</th>)}</tr></thead>
      <tbody>
        {table.rows.map((row) => (
          <tr className="border-t border-slate-700" key={row.state}>
            <td className="p-2">{row.start ? "→" : ""}{row.accepting ? "*" : ""}{row.state}</td>
            {table.alphabet.map((symbol) => <td className="p-2" key={symbol}>{row.cells[symbol]?.join(", ") || "—"}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
