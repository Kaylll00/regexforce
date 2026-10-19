export function Disclaimer() {
  return <p className="rounded-xl border border-amber-700/60 bg-amber-950/40 p-4 text-sm leading-6 text-amber-100">
    The Pumping Lemma gives a necessary condition for regular languages. It can be used to show that a language is not regular. Failing or passing a pumping attempt never proves a language is regular, and testing many strings never establishes regularity.
  </p>;
}
