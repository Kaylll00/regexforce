import type { Step } from "@/lib/types";

type Props = {
  accepted: boolean;
  forms: string[] | null;
  steps?: Step[];
};

export function DerivationViewer({ accepted, forms, steps = [] }: Props) {
  if (!accepted || !forms) {
    return <p className="rounded border border-red-800 bg-red-950/40 p-3 text-red-200">The string is not derivable from this grammar.</p>;
  }
  return (
    <div className="space-y-2">
      <p className="text-emerald-300">Derivation found</p>
      <ol className="space-y-2">
        {forms.map((form, index) => (
          <li className="rounded bg-slate-950 p-2 font-mono text-sm" key={`${form}-${index}`}>
            {form || "ε"}
            {steps[index] && <span className="ml-3 font-sans text-xs text-slate-400">{steps[index].description}</span>}
          </li>
        ))}
      </ol>
    </div>
  );
}
