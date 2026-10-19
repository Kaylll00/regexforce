# RegexForge — Phase-by-Phase Build Plan (for the AI assistant)

Product spec: `RegexForge.md` (the WHAT). This file is the HOW: exact order, files, signatures, contracts, tests.
If the two files disagree on *how* to build something, **this file wins**. On *what* to build, `RegexForge.md` wins.

---

## 0. Rules of engagement

1. Read this entire file and `RegexForge.md` before writing any code.
2. Work **one phase at a time, in order**. A phase is finished only when **all** of these hold:
   - every task in the phase is implemented;
   - the phase's tests pass (`python -m pytest` and/or `npm run test`);
   - lint is clean (`ruff check .` in `backend`; `npm run lint` and `npx tsc --noEmit` in `frontend`);
   - the phase's **Done when** checklist is satisfied.
3. After finishing a phase: append an entry to `PROGRESS.md` (what was built, test counts, deviations), then `git add .`, `git commit -m "phase N: <summary>"`, `git push`. Then start the next phase **without asking permission**.
4. **Resume protocol:** at the start of every session, read `PROGRESS.md` and continue from the first unfinished phase. Never redo finished phases.
5. Do not ask the user questions you can answer with the defaults in this file. Record any deviation in `PROGRESS.md`.
6. If blocked by the environment (a package will not install, a port is busy, the database is unreachable), **stop and report the exact error to the user**. Do **not** work around it by changing the Python version, using `--force` / `--legacy-peer-deps`, or passing `--allow-scripts` on the command line.
7. Never commit secrets. `backend/.env` and `frontend/.env.local` already exist; never overwrite or commit them. Create `.env.example` files instead (Phase 0).
8. **The formal engine is hand-written.** Forbidden for core logic: `automata-lib`, `greenery`, `pyformlang`, `interegular`, or any automata/regex-algebra library. Do not use Python's `re` module to evaluate user regexes or to implement the lexer. Allowed: stdlib, FastAPI/SQLAlchemy/Pydantic, ReportLab (reports), Hypothesis/pytest (tests).
9. Every engine algorithm returns `(result, steps)` where `steps` is a `list[Step]` (Section 3.2). No algorithm may be a black box.
10. Honesty rules (also shown in the UI, see Phase 11): never claim that testing many strings proves regularity; never claim the Pumping Lemma is a complete test for regularity; never claim the system can prove arbitrary user claims.

---

## 1. Current state (already done — do NOT redo)

- Project root: `regexforge/` (Windows, PowerShell). Git repo exists, branch `master`, remote `origin` (GitHub). Use plain `git push`.
- Root `.gitignore` exists (ignores `.venv`, `__pycache__`, `.env`, `.env.local`, etc.). `frontend/.gitignore` was created by Next.js.
- PostgreSQL 18 is installed and running locally; database **`regexforge`** exists.
- `backend/`: virtual environment at `backend/.venv`, dependencies from `requirements.txt` / `requirements-dev.txt` installed (FastAPI, uvicorn, Pydantic, SQLAlchemy, Alembic, psycopg, python-dotenv, ReportLab, pytest, pytest-cov, Hypothesis, httpx, ruff, mypy). Folders `app/`, `engine/`, `tests/` exist. `backend/.env` exists (`DATABASE_URL`, `CORS_ORIGINS`).
- `backend/app/main.py` exists: FastAPI app with CORS from `CORS_ORIGINS` and `GET /health` → `{"status":"ok"}`. **Keep `/health`.**
- `frontend/`: Next.js (App Router, TypeScript, ESLint, Tailwind, `src/` directory, npm) created with `create-next-app`. `frontend/.env.local` exists (`NEXT_PUBLIC_API_URL=http://localhost:8000`). Packages installed: `@xyflow/react`, `zustand`, `@tanstack/react-query`, and dev packages `vitest`, `@vitejs/plugin-react`, `jsdom`, `@testing-library/react`, `@testing-library/jest-dom`, `@types/node@24`. npm `allowScripts` approval for `unrs-resolver` is stored in `frontend/package.json`.
- **Verify, don't assume** (Phase 0 does this): run `npm ls vitest` in `frontend`. If vitest is missing, run `npm install -D @types/node@24` and then `npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom`.

Environment notes:
- Python is 3.14, Node is 24, npm is recent with install-script blocking. If npm warns that an install script was blocked, review with `npm install-scripts ls` and approve with `npm install-scripts approve <pkg>` (this edits `allowScripts` in `package.json`).
- Read `frontend/AGENTS.md` if it exists and follow it. This is a recent Next.js major version: do not rely on memory of older Next.js APIs; check the installed version's docs/types when unsure.
- Use whichever Tailwind version the scaffold installed. Do not downgrade or switch it.

---

## 2. Conventions

### 2.1 Commands (PowerShell, Windows)

```
# backend (venv must be active; if not: cd backend; .venv\Scripts\activate)
cd backend
python -m pytest                 # run tests
python -m pytest --cov=engine    # with coverage
ruff check .                     # lint
mypy engine                      # type check (engine only)
uvicorn app.main:app --reload --port 8000

# frontend
cd frontend
npm run dev                      # http://localhost:3000
npm run test                     # vitest
npm run lint
npx tsc --noEmit
npm run build
```

Run backend commands from `backend/`. Run frontend commands from `frontend/`. Run git commands from the project root.

### 2.2 Python style

- Python 3.11+ syntax, full type hints, `from __future__ import annotations` not required.
- Top-level packages under `backend/` are `engine` and `app`. Import like `from engine.regex.parser import parse`. (Phase 0 configures pytest so this works.)
- `engine/` must **never** import FastAPI, SQLAlchemy, Pydantic, or anything from `app/`.
- Data classes: `@dataclass(frozen=True)`. Never hash automata (they contain dicts).
- Every public function has a 1–3 line docstring naming the algorithm.
- **Determinism:** all iteration over states/symbols uses `natural_sorted(...)` (sorts `q2` before `q10`; implemented in `engine/util.py`). Alphabets are sorted lists. This keeps steps, state names and tests stable.
- Safety limits (raise `EngineError` with a clear message): regex length ≤ 500 chars; any constructed DFA ≤ 2000 states; steps per operation ≤ 500 (if exceeded, keep the first 499 and append one final Step titled "Output truncated").

### 2.3 TypeScript style

- `strict` TypeScript, no `any`. Client components start with `"use client"`.
- JSON keys from the API are **snake_case**; TypeScript types mirror them exactly (no key conversion).
- Tailwind for styling. The starter is dark; support dark mode and keep sufficient contrast.
- Components in `src/components`, pure helpers in `src/lib`, pages in `src/app/<route>/page.tsx`.

### 2.4 Commit messages

`phase N: <short summary>` (for example `phase 2: automata core with Thompson, subset construction, minimization`).

---

## 3. Shared contracts (implement exactly; every later phase depends on them)

### 3.1 Errors — `engine/errors.py`

```python
class EngineError(Exception):            # base; has .code (str) and optional .position (int | None)
class RegexSyntaxError(EngineError)      # code "regex_syntax"; position = 0-based index in the input
class UnsupportedFeatureError(EngineError)  # code "unsupported_feature"; position
class AutomatonError(EngineError)        # code "automaton_invalid"
class GrammarError(EngineError)          # code "grammar_invalid"; position = line number (1-based)
class LimitError(EngineError)            # code "limit_exceeded"
```

### 3.2 Step — `engine/steps.py`

```python
@dataclass(frozen=True)
class Step:
    title: str                       # short, e.g. "Eliminate state q2"
    description: str                 # one or two plain-English sentences
    data: dict[str, Any]             # JSON-serializable extra detail, may be {}
    kind: str = "info"               # "info" | "valid_argument" | "numeric_demonstration" | "warning"
    def to_dict(self) -> dict: ...
```

Also in `engine/util.py`: `natural_sorted(items)`, `cap_steps(steps) -> list[Step]` (applies the 500-step cap).

### 3.3 Regex AST — `engine/regex/ast.py`

Frozen dataclasses: `Empty`, `Epsilon`, `Symbol(char: str)`, `Union(left, right)`, `Concat(left, right)`, `Star(inner)`; alias `Node`.
Helpers: `alphabet_of(node) -> frozenset[str]`, `to_dict(node)` / `from_dict(d)` (JSON like `{"type":"union","left":{...},"right":{...}}`, types: `empty, epsilon, symbol, union, concat, star`). `Symbol` must be exactly one character and may not be `ε` or `∅`.

### 3.4 Automaton model — `engine/automata/model.py`

```python
EPSILON = "ε"

@dataclass(frozen=True)
class NFA:
    states: frozenset[str]; alphabet: frozenset[str]; start: str
    accepting: frozenset[str]
    transitions: dict[tuple[str, str], frozenset[str]]   # (state, symbol-or-EPSILON) -> targets
    labels: dict[str, tuple[str, ...]]                   # optional display info, default {}

@dataclass(frozen=True)
class DFA:                                               # same fields, but:
    transitions: dict[tuple[str, str], str]              # (state, symbol) -> target; may be partial
```

Both have `validate()` (raise `AutomatonError` if: start not in states; accepting not subset of states; a transition references an unknown state or a symbol outside the alphabet; DFA contains ε), `to_dict()` and `from_dict()`.

**Automaton JSON** (used by the API, import/export, and the frontend):

```json
{
  "type": "nfa",
  "alphabet": ["a", "b"],
  "states": ["q0", "q1"],
  "start": "q0",
  "accepting": ["q1"],
  "transitions": [{"from": "q0", "symbol": "a", "to": "q1"}],
  "labels": {"d0": ["q0", "q1"]}
}
```

- `type` is `"nfa"` or `"dfa"`. ε transitions use the symbol `"ε"`. `labels` is optional.
- Lists are sorted (natural order). Transitions are sorted by `(from, symbol == "ε", symbol, to)`.
- `from_dict` must reject: unknown `type`, missing keys, duplicate states, DFA with two targets for one `(state, symbol)`.

**Transition table JSON** — `transition_table(automaton) -> dict`:

```json
{
  "alphabet": ["a", "b"],
  "has_epsilon": false,
  "rows": [
    {"state": "q0", "start": true, "accepting": false,
     "cells": {"a": ["q1"], "b": []}}
  ]
}
```
`cells` includes an `"ε"` key only when `has_epsilon` is true. Empty list means no transition.

### 3.5 Simulation result — `engine/automata/simulate.py`

```python
@dataclass(frozen=True)
class SimStep:
    index: int                       # 0 = initial configuration (after ε-closure of start)
    symbol: str | None               # None for index 0
    before: tuple[str, ...]          # active states before reading the symbol (sorted)
    after: tuple[str, ...]           # active states after reading it and taking ε-closure (sorted)
    via_epsilon: tuple[str, ...]     # states added by ε-closure in this step
    note: str                        # human-readable explanation of this step

@dataclass(frozen=True)
class SimulationResult:
    accepted: bool
    steps: tuple[SimStep, ...]
    reason: str                      # why accepted/rejected, human-readable
    rejected_at: int | None          # index of the step where it died, else None
```

Reason strings (use these formats):
- accepted: `Accepted: ended in accepting state q3.`
- ended in non-accepting: `Rejected: ended in {q1, q2}, none of which is accepting.`
- DFA missing transition: `Rejected: no transition from q2 on 'b'.`
- NFA dead end: `Rejected: no state in {q1, q2} can read 'b'.`
- symbol not in alphabet: `Rejected: symbol 'x' is not in the alphabet {a, b}.`

### 3.6 Rule input (used by Phases 5, 6, 10)

A "rule" is one of:

```json
{"kind": "regex", "regex": "(a|b)*abb", "textbook": false}
{"kind": "automaton", "automaton": { ...Automaton JSON... }}
{"kind": "grammar", "grammar": "S -> aS | bS | abb"}
```
Optional top-level `alphabet` (list of single characters) extends the alphabet inferred from the rule.

### 3.7 API error body (Phase 6)

All `EngineError`s return HTTP **422** with:
```json
{"error": {"code": "regex_syntax", "message": "Unmatched '(' at position 3.", "position": 3}}
```
`position` is `null` when not applicable.

---

## 4. Phases

---

### Phase 0 — Preflight and skeleton

**Goal:** confirm the environment and create all folders/config so later phases only add code.

**Tasks**
1. Run the verification commands: `python --version`, `node --version`, `psql --version`, `npm ls vitest` (in `frontend`), `python -m pip list` (in `backend` with venv). Fix only what the "Current state" section says to fix.
2. Create package skeleton with empty `__init__.py` files:
   ```
   backend/engine/{__init__,errors,steps,util}.py
   backend/engine/regex/__init__.py
   backend/engine/automata/__init__.py
   backend/engine/conversion/__init__.py
   backend/engine/grammar/__init__.py
   backend/engine/analysis/__init__.py
   backend/engine/proofs/__init__.py
   backend/app/__init__.py  backend/app/api/__init__.py  backend/app/db/__init__.py
   backend/app/schemas/__init__.py  backend/app/services/__init__.py
   backend/tests/__init__.py  backend/tests/engine/__init__.py  backend/tests/api/__init__.py
   ```
3. Implement Sections 3.1 and 3.2 (`errors.py`, `steps.py`, `util.py` with `natural_sorted` and `cap_steps`) with unit tests in `backend/tests/engine/test_util.py`.
4. Create `backend/pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   pythonpath = ["."]
   addopts = "-q"

   [tool.ruff]
   line-length = 100

   [tool.mypy]
   ignore_missing_imports = true
   ```
5. Frontend test setup:
   - `frontend/vitest.config.ts`: plugin `@vitejs/plugin-react`, `test.environment = "jsdom"`, `test.setupFiles = ["./src/test/setup.ts"]`, `resolve.alias["@"] = path.resolve(__dirname, "src")`.
   - `frontend/src/test/setup.ts`: `import "@testing-library/jest-dom/vitest"`.
   - `package.json` scripts: `"test": "vitest run"`, `"test:watch": "vitest"`.
   - One trivial passing test `src/lib/smoke.test.ts` to prove the runner works.
6. Create `backend/.env.example` (`DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/regexforge`, `CORS_ORIGINS=http://localhost:3000`) and `frontend/.env.example` (`NEXT_PUBLIC_API_URL=http://localhost:8000`).
7. Create `PROGRESS.md` at the project root:
   ```
   # Progress log
   | Phase | Status | Notes |
   |---|---|---|
   | 0 | pending | |
   ... one row per phase 0–12
   ```
   and fill in row 0 when done.
8. Create a stub root `README.md` (title and one line; completed in Phase 12).

**Done when:** `python -m pytest` and `npm run test` both pass; `ruff check .` clean; `GET /health` still works; commit `phase 0: skeleton, config, shared contracts`.

---

### Phase 1 — Regex parser, AST, printer, reference matcher

**Goal:** a correct, well-tested parser for the formal regex syntax, plus an independent reference matcher used by every later test.

**Formal syntax**

| Construct | Syntax |
|---|---|
| Symbol | any single character that is not reserved |
| Union | `\|` (default mode). In **textbook mode** (`textbook=True`) `+` is also union. |
| Concatenation | implicit (`ab`) |
| Kleene star | `*` |
| Grouping | `( … )` |
| Epsilon | `ε` or `\e` |
| Empty language | `∅` or `\0` |
| Escape | `\` followed by any character makes it a literal symbol (e.g. `\|`, `\*`, `\(`, `\\`, `\ ` for a space). Exceptions: `\e` = ε, `\0` = ∅. |
| Sugar (default mode only) | `r+` ⇒ `rr*`, `r?` ⇒ `(r\|ε)` (in textbook mode only `?` is sugar). Each desugaring emits a `Step`. |

Whitespace (space, tab) outside an escape is ignored. Precedence (high → low): star/sugar, concatenation, union. Binary operators are left-associative.

**Rejected with `UnsupportedFeatureError`** (message must explain it is outside classical regular expressions and what to do instead):
- unescaped `.` `[` `]` `{` `}` `^` `$`;
- backreferences `\1`…`\9`;
- groups beginning `(?` (lookahead, lookbehind, non-capturing, named);
- a quantifier directly followed by `?` or `+` that would form a lazy/possessive quantifier (`*?`, `+?`, `??`, `*+`, `++`, `?+`). In textbook mode `+` is the union operator, so only a quantifier followed by `?` is flagged there (`*?`, `??`).

**Rejected with `RegexSyntaxError`** (always with a 0-based `position`): unmatched `(` or `)`, empty operand (`|a`, `a|`, `()`, a leading `*`), trailing backslash.

**Files and signatures**

```
engine/regex/ast.py          # Section 3.3
engine/regex/lexer.py        # Token(kind, value, start, end); tokenize(text, *, textbook=False) -> list[Token]
engine/regex/parser.py       # parse(text: str, *, textbook: bool = False) -> tuple[Node, list[Step]]
engine/regex/printer.py      # to_string(node: Node) -> str
engine/regex/highlight.py    # highlight_tokens(text, *, textbook=False) -> list[Token]   (never raises)
engine/regex/derivative.py   # nullable(node) -> bool; derive(node, ch) -> Node; matches(node, s) -> bool
```

- Token kinds: `symbol, union, star, plus, qmark, lparen, rparen, epsilon, empty, error`. Escaped characters are `symbol` tokens with `value` equal to the literal character and `end - start == 2`.
- `highlight_tokens` never raises: invalid or unsupported characters become `error` tokens.
- Printer: `ε`, `∅`, `a|b`, `ab`, `a*`; minimal parentheses assuming left-associativity (a right child of the same operator type is parenthesized); escapes reserved characters with `\`. Property: `parse(to_string(n))[0] == n` for every AST `n`.
- Derivative matcher (Brzozowski): `d(Symbol c, c)=ε`, `d(Symbol c, x≠c)=∅`, `d(∅)=d(ε)=∅`, `d(r|s)=d(r)|d(s)`, `d(rs)=d(r)s | (d(s) if nullable(r))`, `d(r*)=d(r)r*`. Apply smart constructors that simplify `∅`/`ε`, deduplicate identical union operands, and collapse `Star(Star(r))` so derivative sizes stay bounded.
- This matcher is **independent of automata** and is the reference oracle for all later correctness tests. Do not reuse automata code in it.

**Tests** (`tests/engine/test_regex_*.py`)
- Precedence (`ab|c*`), escapes, ε/∅ forms, sugar steps, textbook mode.
- Every rejection case above, with the exact `position` where applicable.
- Round trip property (Hypothesis strategy `regex_asts(alphabet="ab", max_depth=4)` in `tests/engine/strategies.py`).
- Matcher truth tables for at least 10 hand-written regexes (including `∅`, `ε`, `(a|b)*abb`, `a*b*`).
- Add `tests/engine/helpers.py` with `all_strings(alphabet, max_len) -> list[str]` (includes the empty string). Reuse it everywhere.

**Done when:** all of the above pass; commit `phase 1: regex parser, printer, reference matcher`.

---

### Phase 2 — Automata core

**Goal:** NFA/DFA models, Thompson construction, simulation with explanations, subset construction, completion, minimization, transition tables.

**Files and signatures**

```
engine/automata/model.py        # Section 3.4 (+ transition_table)
engine/automata/thompson.py     # regex_to_nfa(node: Node, alphabet: Iterable[str] | None = None) -> tuple[NFA, list[Step]]
engine/automata/simulate.py     # simulate(automaton: NFA | DFA, string: str) -> SimulationResult
engine/automata/nfa_ops.py      # epsilon_closure(nfa, states) -> frozenset[str]
                                # remove_epsilon(nfa) -> tuple[NFA, list[Step]]
                                # reverse_nfa(nfa) -> NFA
                                # dfa_to_nfa(dfa) -> NFA
engine/automata/subset.py       # nfa_to_dfa(nfa) -> tuple[DFA, list[Step]]
engine/automata/dfa_ops.py      # remove_unreachable(dfa) -> tuple[DFA, list[Step]]
                                # complete_dfa(dfa, alphabet=None) -> tuple[DFA, list[Step]]
                                # minimize_dfa(dfa, trim_dead: bool = False) -> tuple[DFA, list[Step]]
```

**Rules**
- **Thompson:** standard fragments with one start and one accepting state, ε-transitions for union/star/concat glue. State names `q0, q1, …` allocated from a counter in construction order. One `Step` per AST node (post-order) describing the fragment built, with `data = {"node": <printed subexpression>, "start": ..., "accept": ...}`. `alphabet = alphabet_of(node) ∪ extra alphabet`.
- **Simulation:** index 0 is the ε-closure of the start state. For a DFA each `before`/`after` has one state. Use the exact reason formats in Section 3.5. A symbol outside the alphabet rejects immediately.
- **Subset construction:** discovery order is BFS over sorted alphabet; new states are named `d0, d1, …`; `labels["d0"]` holds the NFA subset. Empty-subset transitions are omitted (the result is a *partial* DFA). One `Step` per DFA state with `data = {"state": "d0", "subset": [...], "accepting": bool, "moves": {"a": "d1", ...}}`. Raise `LimitError` beyond 2000 DFA states.
- **`complete_dfa`:** adds a dead state named `dead` (if taken, `dead1`, …) only if some transition is missing. Alphabet defaults to the DFA's own; a larger alphabet adds missing columns.
- **`minimize_dfa`:** remove unreachable states, complete the DFA, then Moore partition refinement. One `Step` per refinement round listing the partition classes (`data = {"round": n, "partition": [[...], ...]}`). Resulting states are named `m0, m1, …` in BFS discovery order with `labels` listing the merged states. `trim_dead=True` removes the dead state and its transitions, producing a partial DFA for display. Document the difference in the docstring.
- **`remove_epsilon`:** `δ'(q,a) = closure(δ(closure({q}), a))`; `q` is accepting iff `closure({q})` contains an accepting state. Result has no ε-transitions and keeps the same state names.

**Tests**
- Hand-checked small cases: `a`, `ab`, `a|b`, `a*`, `(a|b)*abb`. The minimized complete DFA of `(a|b)*abb` has exactly **4** states.
- Simulation reason strings for each case in Section 3.5.
- **Language preservation property** (Hypothesis + `all_strings("ab", 5)`): for every random AST, the derivative matcher, the NFA, the subset DFA, the completed DFA, and the minimized DFA accept exactly the same strings.
- `transition_table` shape and ε column behavior; `from_dict`/`to_dict` round trip; every `AutomatonError` case.
- Reversal: `reverse_nfa` accepts `reverse(w)` iff the original accepts `w`.

**Done when:** all pass; mypy clean on `engine`; commit `phase 2: automata core`.

---

### Phase 3 — Conversions (automaton → regex)

**Goal:** both required explainable methods plus simplification.

**Files and signatures**

```
engine/conversion/simplify.py            # simplify(node: Node) -> Node
engine/conversion/state_elimination.py   # automaton_to_regex_state_elimination(a: NFA | DFA) -> tuple[Node, list[Step]]
engine/conversion/arden.py               # automaton_to_regex_arden(a: NFA | DFA) -> tuple[Node, list[Step]]
engine/conversion/pipeline.py            # build_pipeline(node, alphabet=None) -> PipelineResult
```

`PipelineResult(nfa, dfa, min_dfa, steps_by_stage: dict[str, list[Step]])` with stage keys `"parse", "nfa", "dfa", "min_dfa"`. `dfa` is the completed subset DFA; `min_dfa` is the minimized complete DFA.

**Simplification rules** (applied bottom-up to a fixpoint; unions are flattened, deduplicated, sorted by printed form, and rebuilt left-associatively):
`∅|r→r`, `r|r→r`, `∅r→∅`, `r∅→∅`, `εr→r`, `rε→r`, `∅*→ε`, `ε*→ε`, `(r*)*→r*`, `ε|r→r` when `nullable(r)`. Docstring must state: the output is correct but **not** guaranteed minimal or readable.

**State elimination (GNFA)**
1. Convert input to an NFA view (ε-edges become `Epsilon` labels). Prune states that are unreachable or cannot reach an accepting state (one `Step`).
2. Add new start `S` with an ε-edge to the old start, and new accept `F` with ε-edges from every old accepting state. Edge labels are regex `Node`s; parallel edges are merged with `Union`.
3. Eliminate original states in order of `(in_degree * out_degree, name)` (natural sort for names). For each removed state `s` and every predecessor `p` and successor `q` (both ≠ `s`): `R(p,q) ← R(p,q) | R(p,s) R(s,s)* R(s,q)`. One `Step` per removed state with `data = {"removed": s, "updates": [{"from": p, "to": q, "formula": "...", "result": "..."}]}`.
4. Result: `simplify(R(S,F))`, or `Empty()` if no edge exists. Final `Step` reports the regex.

**Arden's theorem**
1. If the input has ε-transitions or nondeterminism, first convert to a DFA (`remove_epsilon` / `nfa_to_dfa` + `remove_unreachable`); record that as a `Step`.
2. Build one equation per state: `X_i = Σ a·X_j ∪ (ε if i is accepting)`. Represent as `{coeffs: {j: Node}, const: Node}` and render with a `format_equation` helper.
3. Process non-start states in natural order, then the start state last. For each state `i`: if the equation contains `X_i` with coefficient `A`, apply Arden (`X = A·X ∪ B ⇒ X = A*·B`); then substitute `X_i` into every other equation that references it. One `Step` per Arden application and one per substitution round (show the equations before/after as strings in `data`).
4. Result: `simplify(const)` of the start state's solved equation, or `Empty()` if every equation is empty.

**Tests**
- Known automata: strings ending in `ab`; even number of `a`s; empty-language automaton → `∅`; only-ε automaton → `ε`; single-state accept-all.
- Property test (Hypothesis, `all_strings("ab", 5)` and the derivative matcher): for random AST `r`, build NFA → regex (both methods) and the resulting regex matches exactly the same strings as `r`.
- Both methods return non-empty `steps` for non-trivial inputs; simplification rules each have a dedicated unit test.

**Done when:** all pass; commit `phase 3: state elimination, Arden, simplification`.

---

### Phase 4 — Regular grammars

**Goal:** parse regular grammars, convert to/from automata and regexes, show derivations.

**Grammar text format**
```
# comment
S -> aS | bA | ε
A -> a | abA
```
- Separator `->` or `→`; alternatives with `|`; blank lines and `#` comments ignored.
- Nonterminals are **single uppercase ASCII letters** `A`–`Z`. Terminals are any other single non-whitespace characters except `|`, `-`, `>`, `→`, `#`. Epsilon is `ε` or `\e`. The start symbol is the head of the first production.
- Allowed shapes (**right-linear**): `A → w`, `A → wB`, `A → ε`, where `w` is a string of terminals (generalized form: several terminals allowed). **Left-linear** is also accepted: `A → w`, `A → Bw`. Mixing left- and right-linear productions, two nonterminals in a body, or a nonterminal in the middle ⇒ `GrammarError` (with the 1-based line number) explaining the grammar is not regular.
- Unit productions `A → B` are allowed.

**Files and signatures**

```
engine/grammar/model.py        # Production(head: str, body: tuple[str, ...]); Grammar(start, productions, kind)
engine/grammar/parser.py       # parse_grammar(text: str) -> tuple[Grammar, list[Step]]
engine/grammar/convert.py      # grammar_to_nfa(g) -> tuple[NFA, list[Step]]
                               # nfa_to_grammar(a: NFA | DFA) -> tuple[Grammar, list[Step]]
                               # grammar_to_regex(g) -> tuple[Node, list[Step]]
                               # regex_to_grammar(node) -> tuple[Grammar, list[Step]]
engine/grammar/derivation.py   # find_derivation(g, string) -> tuple[list[str] | None, list[Step]]
engine/grammar/printer.py      # grammar_to_text(g) -> str
```
`Grammar.kind` is `"right-linear"` or `"left-linear"` (terminal-only grammars are `"right-linear"`).

**Rules**
- **Right-linear → NFA:** one state per nonterminal plus an accepting state `F`. `A → w B` adds a chain of transitions reading `w` from `A` to `B` (insert intermediate states named `A.p<k>.<i>` when `|w| > 1`); `A → w` goes to `F`; `A → ε` adds an ε-transition `A → F`. One `Step` per production.
- **Left-linear → NFA:** reverse every production body, treat the result as a right-linear grammar of the reversed language, build its NFA, then apply `reverse_nfa`. Record this as `Step`s.
- **Automaton → grammar:** first `remove_epsilon` (NFA) or use the DFA directly. Name states in BFS order `S, A, B, C, …` (skip `S` after the start). For each transition `p -a-> q` add `P → aQ`; for each accepting `p` add `P → ε`. If more than 26 states are needed, or the alphabet contains uppercase letters, raise `GrammarError` suggesting minimization or a different alphabet.
- **`grammar_to_regex`:** grammar → NFA → state elimination. **`regex_to_grammar`:** regex → NFA → minimize → `nfa_to_grammar`.
- **Derivation:** `find_derivation` returns the list of sentential forms, e.g. `["S", "aA", "abB", "abb"]`, or `None` if the string is not in the language. Search the states `(consumed_length, nonterminal)` with a visited set (unit-production cycles must not loop). Because linear grammars have at most one nonterminal per form, the derivation is both leftmost and rightmost; mention this in a `Step`. Left-linear grammars are searched from the end of the string. One `Step` per production applied with `data = {"production": "A -> aB", "form": "aB"}`.

**Tests**
- Parse valid/invalid grammars (every `GrammarError` case, line numbers).
- Round trips: regex → grammar → regex and automaton → grammar → NFA preserve the language (`all_strings("ab", 5)` + derivative matcher).
- Property: `find_derivation(g, w) is not None` iff the NFA from `grammar_to_nfa(g)` accepts `w`, for all strings ≤ 5 and several hand-written grammars (right-linear, left-linear, with unit productions, with multi-terminal bodies).

**Done when:** all pass; commit `phase 4: regular grammars`.

---

### Phase 5 — Language analyzer

**Goal:** closure operations, equivalence with verified counterexamples, emptiness/finiteness, and multi-rule comparison.

**Files and signatures**

```
engine/analysis/rules.py         # resolve_rule(rule: dict, alphabet: Iterable[str] | None = None) -> tuple[DFA, list[Step]]
engine/analysis/align.py         # align(a: DFA, b: DFA, extra_alphabet=None) -> tuple[DFA, DFA]   (complete, same alphabet)
engine/analysis/product.py       # product(a, b, accept: Callable[[bool, bool], bool]) -> tuple[DFA, list[Step]]
engine/analysis/closure.py       # apply_closure(op: str, operands: list[DFA], minimize: bool = True) -> tuple[DFA, list[Step]]
engine/analysis/equivalence.py   # check_equivalence(a: DFA, b: DFA) -> EquivalenceResult
engine/analysis/properties.py    # is_empty, is_universal, is_finite, shortest_accepted
                                 # is_subset(a, b) -> tuple[bool, str | None]; overlap(a, b) -> str | None
                                 # compare(a, b) -> RelationResult
engine/analysis/rules_set.py     # compare_many(rules: list[tuple[str, DFA]]) -> ComparisonReport
```

**Rules**
- `resolve_rule` handles the three rule kinds in Section 3.6, returning a **complete minimized DFA** over the combined alphabet.
- **Operations** (`op` names): `union`, `intersection`, `difference`, `symmetric_difference`, `complement`, `concatenation`, `star`, `reversal`. Binary ops on DFAs use `product` with reachable-pairs-only exploration (states named `p0, p1, …`; `labels` hold the pairs; one `Step` per explored pair). `complement` flips accepting states of the **complete** DFA. `concatenation`, `star`, `reversal` build an NFA, then `nfa_to_dfa` and (if `minimize`) `minimize_dfa`.
- **Equivalence:** align alphabets, build the symmetric-difference product (accept when exactly one side accepts), BFS from the start over the **sorted alphabet** to find the **shortest** accepted string (ties broken by alphabet order). `EquivalenceResult(equivalent: bool, counterexample: str | None, a_accepts: bool | None, b_accepts: bool | None, steps)`. **Mandatory self-check:** simulate the counterexample on both original DFAs and confirm they disagree; if not, raise an internal `EngineError("equivalence self-check failed")`. The empty string is a valid counterexample; represent it as `""` (UI shows `ε`).
- **Properties:** `is_finite` trims to useful states (reachable **and** co-reachable) and checks for a cycle among them; `is_universal` = complement is empty; `shortest_accepted` returns `None` for the empty language.
- **`compare(a, b)`** returns relation in `{"equivalent", "a_subset_b", "b_subset_a", "overlapping", "disjoint"}` with witnesses: for subset relations a string in the larger-only side; for overlapping, one string in the intersection and one in each difference; for disjoint, none.
- **`compare_many`:** returns the pairwise relation matrix and a `redundant` list. Rule `i` is redundant if some other rule `j` has `L(i) ⊆ L(j)` and (`L(i) ≠ L(j)` or `j < i`) — so equal duplicates flag only the later one. Each entry reports the rule it is covered by.

**Tests**
- Known equivalent pairs: `(a|b)*` vs `(a*b*)*`; `a(ba)*` vs `(ab)*a`; `(a|b)*abb` vs itself minimized.
- Known inequivalent pairs with the exact expected shortest counterexample (`(a|b)*abb` vs `(a|b)*ab` → `ab` accepted only by the second).
- Closure properties on `all_strings("ab", 5)`: `L(A∪B)=L(A)∪L(B)`, intersection, difference, `L(¬A)=Σ*\L(A)`, concatenation, star, reversal, checked against the derivative matcher.
- Hypothesis: for random ASTs `r`, `check_equivalence(rule(r), rule(regex_from_automaton(rule(r))))` says equivalent (this strengthens Phase 3's round trip).
- Emptiness/finiteness/universality edge cases (`∅`, `ε`, `a*`, `(a|b)*`, `a|b`); `compare_many` redundancy rules including equal duplicates.

**Done when:** all pass; commit `phase 5: language analyzer`.

---

### Phase 6 — Backend API and persistence

**Goal:** expose the engine through FastAPI and persist projects/rules/test sets.

**Files**
```
app/main.py                    # include routers, exception handlers, keep /health
app/api/{regex,automata,grammar,analysis,projects}.py
app/schemas/*.py               # Pydantic request/response models
app/services/engine_service.py # thin glue; converts engine objects <-> JSON
app/db/{base,models,session}.py
backend/alembic.ini, backend/alembic/ (migrations)
```

**Request validation limits (Pydantic):** regex ≤ 500 chars; `strings` ≤ 500 items, each ≤ 200 chars; automaton ≤ 500 states and ≤ 5000 transitions; grammar ≤ 5000 chars; alphabet ≤ 64 single characters.

**Error handling:** register an exception handler for `EngineError` returning HTTP 422 with the body in Section 3.7. Keep FastAPI's default validation error shape for malformed requests.

**Endpoints** (all `POST` unless noted; all responses include `steps` as `[{title, description, data, kind}]` where applicable)

| Path | Request | Response |
|---|---|---|
| `/api/regex/parse` | `{regex, textbook?}` | `{canonical, ast, alphabet, tokens:[{kind,value,start,end}], steps}` |
| `/api/regex/build` | `{regex, textbook?, alphabet?}` | `{canonical, alphabet, nfa, dfa, min_dfa, tables:{nfa,dfa,min_dfa}, steps_by_stage}` |
| `/api/automata/validate` | `{automaton}` | `{automaton (normalized), table}` |
| `/api/automata/simulate` | `{automaton, strings[]}` | `{results:[{string, accepted, steps:[SimStep], reason, rejected_at}]}` |
| `/api/automata/to-dfa` | `{automaton}` | `{automaton, table, steps}` |
| `/api/automata/complete` | `{automaton, alphabet?}` | `{automaton, table, steps}` |
| `/api/automata/minimize` | `{automaton, trim_dead?}` | `{automaton, table, steps}` |
| `/api/automata/to-regex` | `{automaton, method: "state_elimination" \| "arden"}` | `{regex, steps}` |
| `/api/grammar/parse` | `{grammar}` | `{kind, productions, canonical, steps}` |
| `/api/grammar/to-automaton` | `{grammar}` | `{nfa, dfa, tables, steps}` |
| `/api/grammar/to-regex` | `{grammar}` | `{regex, steps}` |
| `/api/grammar/from-regex` | `{regex, textbook?}` | `{grammar, steps}` |
| `/api/grammar/from-automaton` | `{automaton}` | `{grammar, steps}` |
| `/api/grammar/derive` | `{grammar, string}` | `{accepted, forms, steps}` |
| `/api/analysis/equivalence` | `{a: Rule, b: Rule, alphabet?}` | `{equivalent, counterexample, a_accepts, b_accepts, steps}` |
| `/api/analysis/closure` | `{operation, operands: Rule[], alphabet?, minimize?}` | `{automaton, table, steps}` |
| `/api/analysis/properties` | `{rule, alphabet?}` | `{empty, finite, universal, shortest_accepted}` |
| `/api/analysis/compare-many` | `{rules:[{name, rule}], alphabet?}` | `{matrix, redundant}` |

**Persistence endpoints** (single-user demo, no authentication)

- `GET/POST /api/projects`; `GET/PUT/DELETE /api/projects/{id}`
- `GET/POST /api/projects/{id}/rules`; `PUT/DELETE /api/rules/{id}`
- `GET/POST /api/projects/{id}/test-sets`; `PUT/DELETE /api/test-sets/{id}`
- `GET/POST /api/projects/{id}/reports` (Phase 12 fills in report generation)

**Database models** (SQLAlchemy 2.0 `Mapped` style, JSON columns via `JSON().with_variant(JSONB(), "postgresql")` so tests can use SQLite):
`Project(id, name, created_at, updated_at)`, `Rule(id, project_id, name, kind, definition, created_at)`, `TestSet(id, project_id, name, strings, created_at)` where `strings` is a list of `{"value": str, "expected": bool | null}`, `AnalysisReport(id, project_id, kind, input_refs, result, created_at)`. Cascade delete from `Project`.

**Alembic:** `alembic init alembic` inside `backend/`. In `alembic/env.py` read `DATABASE_URL` from the environment (load `.env` with python-dotenv) and set `target_metadata = Base.metadata`. Generate the first revision with autogenerate and run `alembic upgrade head` against the `regexforge` database.

**Tests** (`tests/api/`, `httpx` + FastAPI `TestClient`)
- One happy-path test per endpoint; error-shape tests (bad regex returns 422 with `code` and `position`; unsupported feature; invalid automaton; grammar error).
- Validation limit tests (oversized regex/strings).
- CRUD tests using an in-memory SQLite engine via a `get_db` dependency override (`StaticPool`). API tests must **not** require PostgreSQL.
- A contract test that `/api/regex/build` for `(a|b)*abb` returns a min DFA with 4 states.

**Done when:** all pass; `uvicorn app.main:app --reload --port 8000` starts; `http://localhost:8000/docs` lists all endpoints; `alembic upgrade head` succeeds on PostgreSQL; commit `phase 6: API and persistence`.

---

### Phase 7 — Frontend foundation and Regex Studio

**Goal:** shared frontend infrastructure and the Regex Studio page.

**Foundation tasks**
1. `src/lib/types.ts`: TypeScript types for every contract in Section 3 (`Step`, `Automaton`, `TransitionTable`, `SimStep`, `SimulationResult`, `Rule`, API error).
2. `src/lib/api.ts`: `apiPost<T>(path, body): Promise<T>` using `NEXT_PUBLIC_API_URL`; throws `ApiError {code, message, position}` for 422 `error` bodies and a generic `ApiError` for network/other failures.
3. `src/app/providers.tsx` (TanStack `QueryClientProvider`) wired into `src/app/layout.tsx`, plus a top navigation bar with links: Home, Studio (`/studio`), Lab (`/lab`), Grammar (`/grammar`), Analyzer (`/analyzer`), Proofs (`/proofs`), Help (`/help`).
4. `src/app/page.tsx`: home page with one card per module and a one-line description. Module routes that are not built yet must render a simple "Coming soon" page so navigation never 404s.
5. Shared components (`src/components`):
   - `AutomatonGraph.tsx` — props `{automaton, activeStates?, activeEdges?, height?}`; uses `@xyflow/react` (import `@xyflow/react/dist/style.css`). States are circles; accepting states have a double ring; the start state has an incoming arrow; ε-edges are dashed; parallel edges between the same pair are merged into one edge with a combined label (`a,b`); opposite-direction edges are curved apart; **self-loops need a custom edge component** (React Flow does not draw them well).
   - `src/lib/layout.ts` — **pure** `layoutAutomaton(automaton) -> {nodes, edges}`: BFS layering from the start state (columns by depth, rows by order within a layer, unreachable states in a final column). Unit-test this function (no React Flow in tests).
   - `StepsPanel.tsx` — collapsible list of `Step`s; renders `data.rows` / `data.updates` / `data.partition` as small tables when present, otherwise pretty-printed JSON; color-codes `kind`.
   - `TransitionTable.tsx` — renders `TransitionTable` JSON, with `→` for the start state and `*` for accepting states.
   - `Disclaimer.tsx` — small reusable notice component.
6. `src/lib/regexTokens.ts` — local TypeScript tokenizer mirroring the Phase 1 token kinds for instant highlighting (unit tests: precedence of escapes, unsupported characters become `error`).
7. `src/lib/simulationEdges.ts` — `edgesForStep(automaton, simStep)` returns the edges taken in that step (symbol edges from `before` to `after`, plus ε-edges for `via_epsilon`).

**Regex Studio page (`/studio`)**
- `RegexEditor.tsx`: textarea with an overlaid highlighted layer (use `regexTokens`), inline error underline at `ApiError.position`, an alphabet field (comma-separated single characters, optional), and a "textbook mode (+ is union)" toggle. Buttons to insert `ε` and `∅`.
- Debounce (400 ms) calls to `/api/regex/build` using TanStack Query; show the parse/unsupported error message under the editor.
- Test string list: add/remove rows; each row has the string, an optional expected verdict (accept / reject / unspecified), and a live badge (accepted ✓ / rejected ✗; mismatch with expected highlighted in red). Live verdicts come from `/api/automata/simulate` on the selected automaton.
- Right pane tabs: **NFA | DFA | Minimal DFA**, each showing `AutomatonGraph`, `TransitionTable`, and that stage's `StepsPanel` (from `steps_by_stage`).
- Step-by-step simulation player for the selected test string: Prev / Next / Play / Reset, highlights `after` states and the edges taken, and shows `SimStep.note` plus the final `reason`. For rejected strings, highlight where it died (`rejected_at`).
- Optional (do last): a minimal **visual regex builder** — buttons that wrap the current selection in `( )`, `*`, or insert `|`, `ε`, `∅`.
- Show a one-line note linking to Help that only classical regex operators are supported.

**Tests (Vitest)**: `layoutAutomaton`, `regexTokens`, `edgesForStep`, `api.ts` error mapping (mock `fetch`), `TransitionTable` render, `StepsPanel` render.

**Done when:** `npm run test`, `npm run lint`, `npx tsc --noEmit`, and `npm run build` all pass; with backend and frontend running, entering `(a|b)*abb` at `/studio` shows NFA, DFA and minimal DFA graphs (min DFA has 4 states); testing `abb`, `aabb`, `ab`, `babb` shows correct verdicts and the step player works; commit `phase 7: frontend foundation and Regex Studio`.

---

### Phase 8 — Automata Lab

**Goal:** build and edit automata visually, run conversions, import/export.

**Tasks**
1. `src/lib/automatonEdit.ts` — **pure** functions on the `Automaton` type: `addState`, `removeState`, `renameState`, `setStart`, `toggleAccepting`, `addTransition(automaton, from, to, symbol)`, `removeTransition`, `setType("nfa" | "dfa")`, `checkDeterminism(automaton) -> string[]` (problems). Unit-test every function. Adding a symbol extends the alphabet; removing the last use of a symbol removes it from the alphabet.
2. `src/lib/labStore.ts` — zustand store holding the current automaton, selection, and the last conversion result.
3. `/lab` page:
   - **Editor:** `AutomatonGraph` in editable mode (draggable nodes; connect handles to create transitions; a small inline input asks for the symbol, with `ε` shortcut; a side panel for the selected state: rename, set start, toggle accepting, delete). Automaton type switch (NFA/DFA); DFA mode shows `checkDeterminism` problems before running anything.
   - **Actions bar:** Validate, NFA→DFA, Complete DFA, Minimize (with "trim dead state" checkbox), To regex (method: State elimination | Arden).
   - **Result area:** shows the result automaton (read-only graph + table) and a **Steps panel** with every algorithm step. A "Use result as current automaton" button copies it into the editor. For To-regex, show the regex in a copyable box and offer "Open in Studio".
   - **Test strings** with the same live verdicts and step player as the Studio (reuse components).
   - **Import / Export:** import JSON by file or pasted text (validate via `/api/automata/validate` and show errors); export downloads `automaton.json` (client-side `Blob`). Also provide "Load example" (a few prebuilt automata).
4. Keep the unsaved-work safety: warn with `beforeunload` when the automaton changed since last export.

**Tests (Vitest):** all `automatonEdit` functions; `labStore` actions; import error path (mock `fetch`).

**Done when:** all frontend gates pass; manually: build an NFA with ε-edges, convert to DFA, minimize, convert to regex via both methods and see the elimination/Arden steps; export then re-import the JSON; commit `phase 8: Automata Lab`.

---

### Phase 9 — Grammar Converter UI

**Tasks** (`/grammar` page)
1. Grammar textarea with live validation (debounced `/api/grammar/parse`); error shows line number and message; show detected kind (right-linear / left-linear) and a normalized view.
2. Actions: **Grammar → automaton** (NFA and DFA graphs, tables, steps), **Grammar → regex** (copyable result, steps), **Regex → grammar** (input box), **Automaton → grammar** (paste automaton JSON or "Use current Lab automaton").
3. **Derivation viewer:** input a string; `/api/grammar/derive`; render `S ⇒ aA ⇒ abB ⇒ abb` with one step per line showing the production used, or a clear "not derivable" message.
4. Examples dropdown (at least 4: right-linear, left-linear, with ε, with multi-terminal bodies). Show the alphabet/uppercase-letter limitation in a short help note.

**Tests (Vitest):** derivation rendering component; error mapping for `grammar_invalid` with line numbers.

**Done when:** frontend gates pass; manual check: example grammar → automaton → regex → grammar round trip works and derivations display; commit `phase 9: Grammar Converter UI`.

---

### Phase 10 — Language Analyzer UI

**Tasks** (`/analyzer` page, tabbed)
1. `RuleEditor.tsx`: a reusable editor for a Rule — kind selector (Regex | Automaton JSON | Grammar), the matching input, an optional shared alphabet field, and inline errors.
2. **Compare tab:** two `RuleEditor`s; button **Check equivalence**. Result banner: Equivalent / Not equivalent. For a counterexample: show it (empty string displayed as `ε`), state which rule accepts and which rejects it, and replay it through **both** automata side by side using the step player (simulate each rule's DFA via the API). Show the algorithm steps.
3. **Operations tab:** operation selector (union, intersection, difference, symmetric difference, complement, concatenation, star, reversal), one or two operands as appropriate, "minimize result" checkbox; shows the result graph, table, and steps; buttons "Copy as automaton JSON" and "Send to Lab".
4. **Properties tab:** one rule → empty? finite? universal? shortest accepted string.
5. **Rule set tab:** an editable list of named rules (name + Rule); optional test strings with expected verdicts; **Compare all** shows the relation matrix (color-coded cells: equivalent, subset, overlap, disjoint; hovering shows witnesses) and a **Redundant rules** list naming what covers each one. Also flags rules whose verdict on a test string contradicts the expected verdict ("incorrect rule" indicator).
6. Persist the rule set to local component state only in this phase (saving to the database arrives in Phase 12).

**Tests (Vitest):** counterexample display (including empty string), matrix color mapping helper, `RuleEditor` kind switching.

**Done when:** frontend gates pass; manual check of the demo cases `(a|b)*` vs `(a*b*)*` (equivalent) and `(a|b)*abb` vs `(a|b)*ab` (counterexample `ab`); commit `phase 10: Language Analyzer UI`.

---

### Phase 11 — Proof Workbench (Advanced)

**Scope limit:** guided templates and a numeric checker. **No** unrestricted theorem proving.

**Engine** (`engine/proofs/`)

```
templates.py   # Template(id, name, description, alphabet, is_regular: bool,
               #          membership: Callable[[str], bool], witness: Callable[[int], str],
               #          outline: tuple[Step, ...])
               # list_templates() -> list[Template]; get_template(id) -> Template
pumping.py     # decompositions(s: str, p: int) -> list[Decomposition]   # all (x,y,z): s=xyz, |xy|<=p, |y|>=1
               # validate_choice(template, p: int, s: str) -> list[str]  # problems: s not in L, |s|<p, bad symbols
               # check_decomposition(template, s, x_len, y_len, i) -> DecompositionCheck
               # check_all(template, s, p, max_i: int = 5) -> PumpingReport
```

Templates (all five required):
1. `anbn` — `{aⁿbⁿ | n ≥ 0}`, non-regular, witness `a^p b^p`.
2. `ww` — `{ww | w ∈ {a,b}*}`, non-regular, witness `a^p b a^p b`.
3. `prime` — `{aⁿ | n is prime}`, non-regular, witness `a^q` with `q` the smallest prime ≥ `p`.
4. `square` — `{a^(n²) | n ≥ 0}`, non-regular, witness `a^(p²)`.
5. `balanced` — balanced parentheses over `{(, )}`, non-regular, witness `(^p )^p`.
Also include **one regular demonstration template** `abstar` — `(ab)*`, `is_regular = True`, witness `(ab)^p`, so users see that pumping attempts *succeed* for regular languages and prove nothing.

Each template's `outline` is a short list of `Step`s (`kind="valid_argument"`) giving the symbolic proof pattern for arbitrary `p` (choose `s`; case-analyse where `y` lies; pick `i`; conclude `xy^iz ∉ L`). Regular template outline explains why pumping cannot show regularity.

`check_all` enumerates every decomposition, and for each tries `i = 0..max_i` (exact membership via the template) to find the smallest `i` with `x y^i z ∉ L`. `PumpingReport(p, s, total, refuted, survivors: list[Decomposition], witness_i: dict, steps, disclaimer)`. Every computed step uses `kind="numeric_demonstration"`. If there are survivors, the report says that *this chosen string does not give a contradiction* and that this proves **nothing** about regularity. If there are none, it says *for this specific p* every decomposition can be pumped out of L, and that a **complete proof requires the symbolic argument for arbitrary p** (point to the outline). `disclaimer` is the constant text:

> "The Pumping Lemma gives a necessary condition for regular languages. It can be used to show that a language is not regular. Failing or passing a pumping attempt never proves a language is regular, and testing many strings never establishes regularity."

**API** (add to Phase 6 routers)
- `GET /api/proofs/templates` → list (id, name, description, is_regular, alphabet, outline steps).
- `POST /api/proofs/pumping/witness` `{template_id, p}` → `{string}`.
- `POST /api/proofs/pumping/decompositions` `{template_id, p, s}` → `{problems, decompositions:[{x,y,z,x_len,y_len}]}`.
- `POST /api/proofs/pumping/check` `{template_id, p, s, x_len?, y_len?, i?}` → single decomposition check if `x_len` is given; otherwise `check_all` report. Limits: `1 ≤ p ≤ 12`, `|s| ≤ 200`, `0 ≤ i ≤ 8`.

**Frontend** (`/proofs`)
- Template picker, `p` selector (1–12), recommended string (from the API) with an optional custom string field and its validity messages.
- Always-visible `Disclaimer` with the constant text above.
- Decomposition table: each row shows `x | y | z`, an input for `i`, a "find i" button, and a result badge (pumped string ∉ L ✓ / ∈ L ✗). A **Check all** button shows the report: counts, survivors, and the verdict wording from above.
- **Outline panel** with the symbolic steps, labeled "Valid argument pattern", clearly separated from computed results labeled "Numeric demonstration for the tested p only".
- Never render any text claiming a language "is regular" or "is proven" based on these checks.

**Tests**
- Backend: decomposition counts for small `p`; every template's `membership` on hand-picked members/non-members; `check_all` shows zero survivors for `anbn` with `p=3` and the recommended witness; shows survivors for `abstar`; `validate_choice` problems; API limits.
- Frontend: verdict wording helper (never outputs "proved regular"), `Disclaimer` always rendered.

**Done when:** all gates pass; manual: `anbn` with `p = 4` and the recommended string shows every decomposition refuted for that `p`; `abstar` shows survivors with the "proves nothing" wording; commit `phase 11: Proof Workbench`.

---

### Phase 12 — Reports, persistence UI, polish, documentation

**Reports (backend)**
- `POST /api/reports/pdf` `{title, regex, textbook?, alphabet?, strings:[{value, expected?}], compare_with?}` builds a PDF with ReportLab: rule definition and canonical form; transition tables for NFA, DFA and minimal DFA; a test-results table (string, expected, actual, match); if `compare_with` is given, the equivalence verdict and counterexample; the algorithm steps for each stage (first 30 per stage). Include small automaton diagrams drawn with `reportlab.graphics` (circular layout, labeled arrows, double ring for accepting states). If diagrams prove too complex, fall back to tables only and note it in `PROGRESS.md`. Do **not** require Graphviz.
- `POST /api/reports/csv` `{kind: "tests" | "transition_table", ...}` returns CSV (`text/csv`) for test results or any transition table.
- `GET /api/reports/{id}/pdf` regenerates a saved report from `AnalysisReport.input_refs`.
- Tests: PDF response starts with `%PDF`, CSV content is parseable, saved report round trip.

**Persistence UI (frontend)**
- A project switcher in the nav (create, rename, delete projects).
- Studio and Analyzer get **Save rule** / **Load rule** and **Save test set** / **Load test set** actions backed by the Phase 6 CRUD endpoints.
- Export buttons: **PDF report** and **CSV** in Studio; CSV for the Analyzer's result tables.

**Polish**
- Loading, empty and error states on every page; disabled buttons during requests; consistent error toast/banner for `ApiError`.
- Keyboard accessibility for the editor, tabs, and step player (Prev/Next with arrow keys); visible focus rings; sufficient contrast.
- `/help` page: supported syntax table, the unsupported-feature list, what each module does, and the **Known limitations** from `RegexForge.md` Section 10 (verbatim meaning).
- Responsive layout: usable at 1280px wide and not broken at 900px.

**Documentation**
- Complete the root `README.md`: project overview, features, architecture diagram (text), and **setup for a new teammate** — install prerequisites (Python 3.11+, Node 20+, Git, PostgreSQL 15+); clone; create database `regexforge`; backend: venv, `pip install -r requirements-dev.txt`, copy `.env.example` to `.env` and set the password, `alembic upgrade head`; frontend: `npm install`, copy `.env.example` to `.env.local`; run backend (`uvicorn app.main:app --reload --port 8000`) and frontend (`npm run dev`); run all tests; note the npm `allowScripts` behavior.
- Optional `scripts/dev.ps1` that prints the two run commands (do not auto-start background processes).

**Final acceptance (do all, report results in `PROGRESS.md`)**
1. `cd backend; python -m pytest --cov=engine` — all pass, engine coverage ≥ 90%. `ruff check .` and `mypy engine` clean.
2. `cd frontend; npm run test; npm run lint; npx tsc --noEmit; npm run build` — all pass.
3. Start backend and frontend; walk the demo flow:
   1. `(a|b)*abb` in Studio → NFA, DFA, minimal DFA (4 states).
   2. Test `abb`, `aabb`, `ab`, `babb`; step through each path; rejection reasons are correct.
   3. In Lab convert the DFA to a regex by state elimination and by Arden; steps are visible.
   4. Analyzer: `(a|b)*` vs `(a*b*)*` → equivalent.
   5. Analyzer: `(a|b)*abb` vs `(a|b)*ab` → counterexample `ab`, replayed side by side.
   6. Analyzer: union of two rules shows a result automaton.
   7. Grammar: right-linear grammar → automaton, plus a derivation.
   8. Proofs: `anbn` walkthrough with the disclaimer visible.
   9. Export a PDF report and a CSV of test results.
4. Confirm `RegexForge.md` Section 8's checklist item by item; list any gaps in `PROGRESS.md`.
5. Confirm no secrets are tracked: `git ls-files | findstr /i ".env"` shows only `.env.example` files.

**Done when:** everything above passes; final commit `phase 12: reports, polish, documentation`; push; write a short summary for the user listing what was built and how to run it.

---

## 5. PROGRESS.md entry template

```
### Phase N — <name>  (date)
- Built: <bullet list>
- Tests: backend <n passed>, frontend <n passed>
- Deviations from BUILD_PHASES.md: <none | list with reason>
- Known issues / follow-ups: <none | list>
```