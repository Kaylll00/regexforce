# RegexForge Demonstration Guide

## Project purpose

RegexForge is an interactive workbench for learning and exploring regular languages. It makes the steps behind regular expressions, finite automata, regular grammars, language operations, and Pumping Lemma examples visible. Use it to experiment with inputs and inspect the generated automata and explanations.

The project has a Next.js frontend, a FastAPI backend, and a Python language-processing engine. The frontend sends operations to the backend; the engine parses inputs and performs the conversions and analyses.

## Start the project locally

Start the backend and frontend in separate terminals. From the repository root, follow the setup steps in `README.md`. The API should respond at `http://localhost:8000/health` with:

```json
{"status":"ok"}
```

Open `http://localhost:3000` to use the app. Keep the backend running while using the interactive features.

## Home

The home page introduces the workbench and links to its main tools. Open a feature card or use the navigation bar to go to Studio, Lab, Grammar, Analyzer, Proofs, or Help.

## Regex Studio

**Purpose:** Enter a regular expression, build its automata, compare the NFA/DFA/minimized DFA, and simulate strings.

1. Enter `a(b|c)*`.
2. Wait for the automata and transition table to update.
3. Select **NFA**, **DFA**, and **Min DFA** to view each version and its explanation steps.
4. Test these strings:

| Input | Expected |
| --- | --- |
| `a` | Accepted |
| `ab` | Accepted |
| `acbc` | Accepted |
| `b` | Rejected |
| `acbd` | Rejected |

Try `a*b` as another expression. It should accept `b`, `ab`, and `aaab`, and reject the empty string and `a`.

The **Textbook mode** checkbox applies the stricter textbook parsing mode. **Export PDF + CSV** downloads a report and the selected automaton's transition table.

## Automata Lab

**Purpose:** Create and edit finite automata, check them, convert between NFA and DFA, minimize them, and simulate input strings.

The default example has start state `q0`, accepting state `q1`, a transition `q0 --a--> q1`, and a `b` loop on `q1`. It recognizes `ab*`.

| Input | Expected |
| --- | --- |
| `a` | Accepted |
| `abbb` | Accepted |
| empty string | Rejected |
| `b` | Rejected |
| `ba` | Rejected |

Try these actions:

1. Click **Load example** to restore the sample automaton.
2. Select a state in the graph and use **Set start**, **Toggle accepting**, **Rename**, or **Delete state**. The graph updates as you edit.
3. Click **Validate** to check the current automaton.
4. Click **NFA → DFA**, **Complete DFA**, or **Minimize** and inspect the resulting graph, transition table, and explanation steps.
5. Choose **State elimination** or **Arden**, then click **To regex** to convert the automaton to a regular expression.
6. Enter `ab` in **Test string** and click **Simulate**. It should be accepted.

To check JSON import, paste this valid DFA into **Import JSON**, then click **Validate and import**:

```json
{
  "type": "dfa",
  "alphabet": ["a"],
  "states": ["q0", "q1"],
  "start": "q0",
  "accepting": ["q1"],
  "transitions": [
    {"from": "q0", "symbol": "a", "to": "q1"}
  ]
}
```

## Grammar Converter

**Purpose:** Parse regular grammars, convert them to automata or regular expressions, convert other representations into grammars, and find derivations.

Paste this right-linear grammar or choose **Right-linear** from the examples:

```text
S -> aA | bS | ε
A -> aA | b
```

The page should show the detected grammar kind and normalized productions. Click **Grammar → automaton** to view the NFA and DFA, or **Grammar → regex** to produce an equivalent expression.

For a derivation, enter `bbaab` in **String to derive** and click **Derive**. A derivation should be found. The string `bba` should not be derivable.

Other grammar examples to try:

```text
S -> aS | ε
```

This generates zero or more `a` symbols. Try deriving `aaa` (accepted) and `aab` (not derivable).

```text
S -> abA | c
A -> aB | ε
B -> b
```

This checks productions with more than one terminal in a body. It can derive `ab`, `abab`, and `c`.

The **Regex → grammar** card accepts a regex such as `(a|b)*abb`. The **Automaton → grammar** card accepts automaton JSON, such as the sample in the Lab section.

## Language Analyzer

**Purpose:** Compare rule languages, apply closure operations, inspect language properties, and compare a named collection of rules.

### Compare

The default rules are `(a|b)*abb` and `(a|b)*ab`. Click **Check equivalence**. They should be reported as not equivalent, with `ab` as a counterexample: Rule B accepts it while Rule A rejects it.

For an equivalent case, enter `a*b` in both Rule A and Rule B, then check again. The result should be **Equivalent**.

### Operations

Use Rule A = `a*`, Rule B = `b*`, and choose **union**. Click **Apply operation** to inspect the resulting automaton and steps. Try **intersection**, **difference**, **complement**, or **star** as well.

### Properties

Enter `a*b` and click **Check properties**. Expected: the language is not empty, is infinite, is not universal, and its shortest accepted string is `b`.

### Rules

Keep the default rules or add a third rule such as `a*`. Click **Compare all** to display pairwise language relations. In **Test rule**, enter `ab` and click **Check verdicts** to simulate it against the rules.

Rule inputs can be regular expressions, regular grammars, or automaton JSON. Use the rule-type menu on each card to switch formats.

## Proof Workbench

**Purpose:** Explore Pumping Lemma proof patterns and run finite checks on decompositions for a selected witness. A numeric check illustrates a chosen value of `p`; it is not by itself a proof for all values.

1. Choose the **{aⁿbⁿ | n ≥ 0}** template and set `p = 3`.
2. The recommended witness should be `aaabbb`.
3. Click **Load decompositions** to list decompositions that satisfy the pumping constraints.
4. Click **Find i** on a row to inspect a pumped result, or **Check all** to inspect every valid decomposition for this `p`.

For this template and `p = 3`, pumping down (choosing `i = 0`) breaks the equal counts for each valid decomposition. The report should show no surviving decompositions. The explanation also reminds you that this finite demonstration does not establish a proof for arbitrary `p`.

Try the **(ab)*** template as a regular-language example. Its recommended witness alternates `a` and `b`; pumping attempts may survive, which is expected for a regular language.

## Help

The Help page provides a quick syntax reference and links to each module. Check it after navigating from a module card to confirm the links work.

## Quick end-to-end checklist

- The backend health endpoint returns `{"status":"ok"}`.
- Studio builds `a(b|c)*` and accepts `acbc`.
- Lab validates the sample automaton and accepts `abbb`.
- Grammar parses the sample and finds a derivation for `bbaab`.
- Analyzer reports the default rules as not equivalent and shows a counterexample.
- Proofs loads decompositions for the `aⁿbⁿ` example with `p = 3`.
- Help links open the corresponding modules.
