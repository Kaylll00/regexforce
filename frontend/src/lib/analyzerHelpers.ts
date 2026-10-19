export type Relation = "equivalent" | "a_subset_b" | "b_subset_a" | "overlapping" | "disjoint";

export function relationLabel(relation: Relation): string {
  return { equivalent: "Equivalent", a_subset_b: "Subset", b_subset_a: "Superset", overlapping: "Overlap", disjoint: "Disjoint" }[relation];
}

export function relationClass(relation: Relation): string {
  return { equivalent: "bg-emerald-900 text-emerald-100", a_subset_b: "bg-blue-900 text-blue-100", b_subset_a: "bg-indigo-900 text-indigo-100", overlapping: "bg-amber-900 text-amber-100", disjoint: "bg-slate-800 text-slate-200" }[relation];
}
