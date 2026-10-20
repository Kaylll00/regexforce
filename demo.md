# RegexForge Panel Demonstration Guide

## 1. Project introduction

**RegexForge** is an explainable toolkit for exploring classical regular languages.
It is designed to show not only the final answer, but also the intermediate
automata, transition tables, derivation steps, and proof-checking results.

The main demonstration flow is:

1. Build a regular expression in **Regex Studio**.
2. Inspect its NFA, DFA, and minimized DFA.
3. Test a string and export a report.
4. Edit and transform an automaton in **Automata Lab**.
5. Convert a regular grammar in **Grammar Converter**.
6. Compare languages in **Language Analyzer**.
7. Demonstrate a Pumping Lemma argument in **Proof Workbench**.
8. Finish with the syntax and limitation guide.

## 2. Before the presentation

Start the backend and frontend in separate terminals:

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm run dev
```

Open `http://localhost:3000`.

Before presenting:

- Confirm that the backend is running on port `8000`.
- Confirm that the frontend is running on port `3000`.
- Keep the browser zoom at 100%.
- Use a wide browser window so graph and table panels are visible.
- Avoid refreshing during a workflow unless you want to reset the current page.

## 3. Opening statement

Use this short introduction:

> RegexForge is an educational formal-language workbench. It accepts classical
> regular expressions and regular grammars, transforms them into finite
> automata, simulates strings, compares languages, and demonstrates proof
> techniques. The main goal is explainability: each module exposes the
> intermediate steps instead of showing only a final result.

The application has five main feature modules:

| Module | Purpose |
| --- | --- |
| Studio | Regex parsing, NFA/DFA construction, minimization, simulation, and reports |
| Lab | Manual automaton editing and automaton conversions |
| Grammar | Grammar parsing, grammar conversions, and derivations |
| Analyzer | Language comparison, closure operations, and language properties |
| Proofs | Guided Pumping Lemma demonstrations |

---

## 4. Demo Part One: Regex Studio

### What it is for

Regex Studio demonstrates the complete regular-expression pipeline:

```text
Regular expression → NFA → DFA → minimized DFA
```

It also lets the presenter simulate a string and export the result.

### Exact steps

1. Click **Studio** in the top navigation.
2. In **Regular expression**, enter:

   ```text
   a(b|c)*
   ```

3. Leave **Textbook mode** unchecked for the first run.
4. Wait briefly for the automata to build.
5. Point out the displayed:
   - Canonical expression
   - Alphabet
   - NFA/DFA/Min DFA selector
   - Automaton graph
   - Transition table
6. Click **NFA**, then **DFA**, then **Min DFA**.
7. Explain that the NFA may contain nondeterministic or epsilon transitions,
   while the DFA has one deterministic transition per symbol and the minimized
   DFA removes equivalent states.

### String simulation

1. In **Test a string**, enter:

   ```text
   abcb
   ```

2. Click **Simulate**.
3. Explain the result:
   - The string is accepted because it begins with `a`.
   - The remaining characters are from `(b|c)*`.
4. Replace the input with:

   ```text
   cb
   ```

5. Click **Simulate** again.
6. Explain that it is rejected because the expression requires the first
   character to be `a`.

### Explainability panel

Scroll to the steps panel and expand it if necessary.

Explain:

> The steps panel makes the algorithm inspectable. Instead of treating the
> automaton as a black box, RegexForge shows how the expression is parsed and
> how the automata are produced.

### Report export

1. Click **Export PDF + CSV**.
2. Explain that the application produces:
   - A PDF report containing the Studio analysis.
   - A CSV transition table for the selected automaton.

### Optional textbook-mode demonstration

1. Check **Textbook mode**.
2. Use:

   ```text
   (a|b)*abb
   ```

3. Compare the canonical expression and construction steps with the previous
   example.

### Panel talking point

> Studio is the main end-to-end feature. It connects syntax, construction,
> formal automata, execution, and documentation in one workflow.

---

## 5. Demo Part Two: Automata Lab

### What it is for

Automata Lab provides direct manipulation of finite automata. It is useful for
showing that RegexForge is not limited to converting expressions; users can also
inspect and edit the automaton itself.

### Exact steps

1. Click **Lab**.
2. Click **Load example**.
3. Point out the graph and the current automaton type.
4. Click **Add state**.
5. In the graph, select a state.
6. In the **Selected state** panel, demonstrate:
   - **Set start**
   - **Toggle accepting**
   - **Rename**
   - **Delete state**
7. Use the graph controls to connect states if needed.
8. Explain that edits are applied to the local automaton model immediately.

### Validation and conversions

1. Click **Validate**.
2. Explain that validation checks whether the automaton has structural issues.
3. If the automaton is an NFA, click **NFA → DFA**.
4. Click **Complete DFA**.
5. Click **Minimize**.
6. Point out the conversion result graph, transition table, and algorithm steps.
7. Click **Use result as current automaton** to continue working with the
   converted result.

### Regex conversion

1. In the method selector, leave **State elimination** selected.
2. Click **To regex**.
3. Point out the generated regex.
4. Click **Copy regex** if you want to show the copy interaction.
5. Click **Open in Studio** to transfer the generated expression to Studio.

### Import and simulation

1. Scroll to **Import JSON**.
2. Paste a valid automaton JSON object if available.
3. Click **Validate and import**.
4. In **Test string**, enter a string and click **Simulate**.
5. Explain that the Lab can both transform an automaton and execute it.

### Panel talking point

> Lab demonstrates the constructive side of automata theory. The user can
> create, modify, validate, convert, minimize, and test a finite automaton
> rather than only viewing an automatically generated one.

---

## 6. Demo Part Three: Grammar Converter

### What it is for

Grammar Converter demonstrates that regular languages can be represented in
multiple equivalent forms:

```text
Regular grammar ↔ finite automaton ↔ regular expression
```

### Parse a grammar

1. Click **Grammar**.
2. Replace the grammar with:

   ```text
   S -> aA | bS | ε
   A -> aA | b
   ```

3. Wait for the parser to update.
4. Point out:
   - Detected grammar kind
   - Normalized productions
   - Syntax guidance

Explain:

> This is a right-linear grammar. Its nonterminals are uppercase letters,
> terminals are single characters, and epsilon represents the empty string.

### Grammar to automaton

1. Click **Grammar → automaton**.
2. Point out the generated NFA.
3. Point out the generated DFA.
4. Compare their transition tables.
5. Expand the steps panel.

Panel explanation:

> The grammar productions are converted into transitions. The resulting
> automata represent the same language as the original regular grammar.

### Grammar to regex

1. Click **Grammar → regex**.
2. Point out the generated regular expression.
3. Explain that this demonstrates equivalence between the grammar and regex
   representations.

### Regex to grammar

1. In **Regex → grammar**, enter:

   ```text
   (a|b)*abb
   ```

2. Click **Convert**.
3. Point out the generated grammar.

### Derivation viewer

1. In **Derivation viewer**, enter:

   ```text
   aab
   ```

2. Click **Derive**.
3. Point out the sequence of sentential forms.
4. Explain that each row shows one derivation step from the start symbol toward
   the requested string.

### Optional rejected derivation

Replace the string with:

```text
bbb
```

Click **Derive** and explain that the viewer reports when the string cannot be
derived from the grammar.

### Panel talking point

> The Grammar module connects syntax and semantics. It shows that the same
> regular language can be studied through productions, automata, and
> expressions.

---

## 7. Demo Part Four: Language Analyzer

### What it is for

The Analyzer focuses on language-level reasoning rather than only construction.
It compares rules, applies closure operations, and reports properties of the
language recognized by a rule.

### Compare two languages

1. Click **Analyzer**.
2. Stay on the **Compare** tab.
3. In **Rule A**, enter:

   ```text
   (a|b)*abb
   ```

4. In **Rule B**, enter:

   ```text
   (a|b)*ab
   ```

5. Click **Check equivalence**.
6. Point out the result:
   - Equivalent or not equivalent
   - Counterexample, if one exists
   - Whether each rule accepts the counterexample
   - Explanation steps

Explain:

> A counterexample is a concrete string that belongs to one language but not
> the other. It is a practical witness that the two languages differ.

### Closure operations

1. Click the **Operations** tab.
2. Use the same two rules.
3. Choose **union**.
4. Click **Apply operation**.
5. Point out the resulting automaton, transition table, and steps.
6. Try **intersection** or **complement** if time allows.
7. Click **Send to Lab** to transfer the generated automaton.

Panel explanation:

> Regular languages are closed under operations such as union, intersection,
> complement, concatenation, star, and reversal. The Analyzer constructs the
> resulting automaton instead of merely stating the theorem.

### Language properties

1. Click **Properties**.
2. Use a simple rule such as:

   ```text
   a*
   ```

3. Click **Check properties**.
4. Point out:
   - Empty
   - Finite
   - Universal
   - Shortest accepted string

### Compare a rule set

1. Click the **Rules** tab.
2. Add another rule with **Add rule**.
3. Enter different expressions in the rule editors.
4. Click **Compare all**.
5. Point out the relation matrix and redundant-rule information.
6. Enter a test string and click **Check verdicts**.

### Panel talking point

> Analyzer moves from individual examples to language relationships. It helps
> students investigate equivalence, closure, redundancy, and basic properties
> experimentally.

---

## 8. Demo Part Five: Proof Workbench

### What it is for

Proof Workbench gives a guided, honest Pumping Lemma demonstration. It is not
an unrestricted theorem prover. It combines a symbolic proof outline with a
numeric checker for a selected pumping length.

### Recommended demonstration

1. Click **Proofs**.
2. Keep the template **L = {aⁿbⁿ | n ≥ 0}** or the template whose name
   corresponds to `a^n b^n`.
3. Leave `p = 3`.
4. Point out the recommended witness string, usually:

   ```text
   aaabbb
   ```

5. Read the disclaimer before running the proof.

### Enumerate decompositions

1. Click **Load decompositions**.
2. Explain the Pumping Lemma decomposition:

   ```text
   s = xyz
   ```

   with constraints:

   ```text
   |xy| ≤ p
   |y| > 0
   ```

3. Point out the decomposition table columns:
   - `x`
   - `y`
   - `z`
   - Pumping exponent `i`
   - Result

### Check individual decompositions

1. Click **Find i** for one row.
2. Point out whether the pumped string remains in the language.
3. Change an `i` value in the table and observe the result.

### Check all decompositions

1. Click **Check all**.
2. Point out:
   - Number of decompositions checked
   - Number refuted
   - Number of survivors
   - Numeric demonstration steps

Explain carefully:

> This checks all valid decompositions for the selected witness and selected
> value of p. It does not by itself prove non-regularity for every possible p.
> The symbolic Pumping Lemma argument is still required.

### Show another template

Use the template selector to show one of:

- `ww`
- `prime`
- `square`
- `balanced`
- `abstar`

Explain that the workbench includes both non-regular demonstrations and a
regular-language example, which helps show the limitations of the lemma.

### Panel talking point

> The Proof Workbench is intentionally transparent about the limits of
> computation. It supports learning the proof structure without claiming that
> a finite numeric experiment is a complete theorem.

---

## 9. Demo Part Six: Help and supported syntax

1. Click **Help**.
2. Show the supported syntax table:

| Input | Meaning |
| --- | --- |
| `a` | Literal symbol |
| `ε` | Empty string |
| `∅` | Empty language |
| `rs` | Concatenation |
| `r|s` | Union |
| `r*` | Kleene star |
| `(r)` | Grouping |

3. Point out the unsupported features:
   - Backreferences
   - Lookaround
   - Character classes
   - Counted repetition
   - Anchors
   - Lazy quantifiers
4. Point out the limitations:
   - Testing strings does not prove regularity.
   - Pumping Lemma checks are not complete regularity tests.
   - Proofs are guided templates.
   - Large inputs are subject to safety limits.

### Panel talking point

> The Help page defines the supported formal language, which prevents users
> from confusing RegexForge's classical regex syntax with the much larger
> feature set of production regex engines.

---

## 10. Suggested 10-minute presentation order

If the panel gives limited time, use this sequence:

| Time | Action |
| --- | --- |
| 0:00–1:00 | Introduce RegexForge and its explainability goal |
| 1:00–3:00 | Studio: build `a(b|c)*`, inspect NFA/DFA/Min DFA |
| 3:00–4:00 | Studio: simulate `abcb` and `cb`, then export reports |
| 4:00–5:30 | Lab: load example, edit a state, validate, minimize |
| 5:30–7:00 | Grammar: parse grammar and convert to automaton/regex |
| 7:00–8:30 | Analyzer: compare two regexes and show a counterexample |
| 8:30–9:30 | Proofs: load decompositions and check all |
| 9:30–10:00 | Explain limitations and close |

## 11. Suggested closing statement

> RegexForge combines formal-language theory with an interactive and
> explainable interface. It does not only answer whether a string is accepted;
> it shows how expressions become automata, how grammars correspond to
> automata and regexes, how languages relate through closure operations, and
> how proof patterns can be explored responsibly. The tool is intended as a
> visual learning and demonstration aid, with its supported syntax and
> computational limitations clearly stated.

## 12. Common panel questions

### Why is this different from a normal regex tester?

Normal regex testers focus on matching strings. RegexForge focuses on
classical formal-language concepts: parsing, NFA/DFA construction,
minimization, grammar conversion, language operations, and proof explanations.

### Why show both NFA and DFA?

An NFA is often easier to construct from a regex. A DFA provides deterministic
execution. Showing both makes the transformation visible and lets the user
connect theory to implementation.

### Why include minimization?

Equivalent DFA states can be merged without changing the language. Minimization
shows that the implementation supports not only construction, but also
optimization and canonicalization of automata.

### Does a rejected test string prove that a language is non-regular?

No. String testing only demonstrates membership or non-membership for that
specific string. Regularity is a property of the whole language.

### Does the Pumping Lemma checker automatically prove non-regularity?

No. It checks finite decompositions for a selected witness and selected
pumping length. The symbolic argument must still quantify over arbitrary
values of `p`.

### What input syntax is supported?

RegexForge intentionally supports classical syntax: literals, epsilon, empty
language, concatenation, union, Kleene star, and grouping. Advanced
production-regex features are intentionally outside the scope.

### What happens if invalid input is entered?

The relevant module displays an error message instead of silently producing an
incorrect result. This is especially visible in Studio, Grammar Converter, and
Proof Workbench.

## 13. Quick input reference

### Regex examples

```text
a(b|c)*
(a|b)*abb
a*
```

### Grammar example

```text
S -> aA | bS | ε
A -> aA | b
```

### Accepted Studio examples

For `a(b|c)*`:

```text
abcb
accc
a
```

### Rejected Studio examples

For `a(b|c)*`:

```text
cb
ba
```

## 14. Important scope note

The project-management controls were intentionally removed from the frontend
because they were not yet complete workspace-loading functionality. The core
RegexForge modules demonstrated in this guide are unaffected.