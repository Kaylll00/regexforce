# RegexForge — Build Instructions for AI Coding Assistant

> **How to use this file:** Read this entire document first, then build the project phase by phase in the order given. Do not skip ahead. After each phase, run the tests for that phase and confirm they pass before moving on. Ask the human only when a decision is genuinely ambiguous; otherwise follow the defaults stated here.

---

## 1. Project Summary

**RegexForge** is an intelligent regular expression analyzer and rule verification studio for developers and computer science students. It does much more than check whether a regex matches a string. It:

- Parses formal regular expressions
- Converts them to NFAs and DFAs
- Visualizes the automata
- Shows the exact transition path for every test string
- Converts automata back into regular expressions (with visible steps)
- Compares two rules for language equivalence and produces a **distinguishing string** when they differ
- Supports regular grammars and guided non-regularity proofs (Pumping Lemma)

Think of it as: **regex debugger + finite automata visualizer + formal verification workbench.**

Theoretical foundation: regular expressions and finite automata are equivalent. The conversion algorithms (Thompson, subset construction, state elimination / Arden's theorem) and automata algorithms (product construction, DFA minimization, complement) power every feature.

---

## 2. Non-Negotiable Design Rules

These come directly from the project proposal. Follow them in every phase.

1. **Build the formal-language engine yourself in Python.** Implement the core algorithms by hand (parser, Thompson construction, subset construction, minimization, state elimination, Arden, product construction, equivalence). Do **not** use third-party automata libraries (e.g. `automata-lib`, `greenery`, `pyformlang`) for the core logic. External libraries are fine for visualization, rendering, PDF export, etc. The algorithms must be readable, testable, and demonstrable to an instructor.
2. **Use a defined mathematical regex syntax** (see Section 6). Clearly separate these formal operators from extra features in programming-language regex engines. Reject unsupported syntax (backreferences, lookaheads, lazy quantifiers) with a clear explanatory error, never silently mis-handle it.
3. **Every mathematical operation must be explainable.** Each algorithm returns a result **plus an ordered list of steps** the UI can display (e.g. state-elimination steps, Arden equation rewrites, subset-construction table, product-construction pairs).
4. **Separate regularity analysis from experimentation.** The software may demonstrate examples and check supported proof steps. It must **never** claim that testing many strings proves regularity, or that the Pumping Lemma is a complete regularity test (it is only a necessary condition for regular languages). Show this disclaimer wherever relevant.
5. **Use automated tests for correctness.** Conversions and closure operations must preserve the recognized language. Use shared string sets, equivalence checks, and property-based tests (Hypothesis).
6. **Do not promise that AI can prove every user claim.** The Proof Workbench checks supported steps and uses templates; it is not an unrestricted theorem prover.

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (App Router), React, TypeScript |
| Automata/flow visualization | React Flow (`@xyflow/react`) |
| Backend API | FastAPI (Python 3.11+) |
| Formal engine | Pure Python package (no web dependencies) |
| Database | PostgreSQL |
| Reports | PDF generation (ReportLab or WeasyPrint) and CSV export |
| Backend testing | pytest (+ Hypothesis for property-based tests) |
| Frontend testing | Vitest (+ React Testing Library) |

---

## 4. Prerequisites to Install First

Verify each is installed; install any that are missing.

- **Python 3.11 or newer** — `python --version`
- **Node.js 20 LTS or newer** and **npm** — `node --version`
- **PostgreSQL 15 or newer** — `psql --version` (or run via Docker: `docker run --name regexforge-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=regexforge -p 5432:5432 -d postgres:16`)
- **Git** — `git --version`
- **Graphviz** (optional, for exporting automaton images server-side) — `dot -V`

---

## 5. Step-by-Step Setup

### Step 1 — Create the project structure

Work inside the current folder. Create this layout:

```
regexforge/
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry
│   │   ├── api/                   # route modules
│   │   ├── db/                    # SQLAlchemy models, session, migrations
│   │   ├── schemas/               # Pydantic models
│   │   └── services/              # glue between API and engine
│   ├── engine/                    # PURE formal-language engine (no web imports)
│   │   ├── regex/                 # lexer, parser, AST, pretty-printer
│   │   ├── automata/              # NFA, DFA, simulation, Thompson, subset, minimize
│   │   ├── conversion/            # state elimination, Arden, regex<->automaton
│   │   ├── grammar/               # regular grammar <-> automaton/regex
│   │   ├── analysis/              # equivalence, closure ops, counterexamples
│   │   ├── proofs/                # pumping lemma templates and step checker
│   │   └── steps.py               # shared "explanation step" data structures
│   ├── tests/
│   │   ├── engine/
│   │   └── api/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── pyproject.toml
└── frontend/                      # created by create-next-app in Step 3
```

### Step 2 — Backend environment and dependencies

```bash
cd regexforge/backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
```

`requirements.txt`:

```
fastapi>=0.115
uvicorn[standard]>=0.30
pydantic>=2.8
sqlalchemy>=2.0
alembic>=1.13
psycopg[binary]>=3.2
python-dotenv>=1.0
reportlab>=4.2
```

`requirements-dev.txt`:

```
-r requirements.txt
pytest>=8.3
pytest-cov>=5.0
hypothesis>=6.108
httpx>=0.27
ruff>=0.6
mypy>=1.11
```

```bash
pip install -r requirements-dev.txt
```

Create `backend/.env`:

```
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/regexforge
CORS_ORIGINS=http://localhost:3000
```

Create a minimal `app/main.py` with a `GET /health` endpoint and CORS enabled for `CORS_ORIGINS`. Confirm it runs:

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Frontend environment and dependencies

```bash
cd regexforge
npx create-next-app@latest frontend --typescript --eslint --app --src-dir --tailwind --use-npm
cd frontend
npm install @xyflow/react zustand @tanstack/react-query
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom
```

Add scripts to `package.json`: `"test": "vitest run"`, `"test:watch": "vitest"`.

Create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Confirm `npm run dev` serves on `http://localhost:3000`.

### Step 4 — Database

1. Create the `regexforge` database if it does not exist.
2. Initialize Alembic in `backend/app/db` and generate the first migration from the models below.
3. Run `alembic upgrade head`.

**Tables (minimum):**

- `projects` — id, name, created_at, updated_at
- `rules` — id, project_id, name, kind (`regex` | `nfa` | `dfa` | `grammar`), definition (JSONB), created_at
- `test_sets` — id, project_id, name, strings (JSONB list of `{value, expected}`)
- `analysis_reports` — id, project_id, kind, input_refs (JSONB), result (JSONB), created_at

### Step 5 — Verify the toolchain

Run `pytest` (should collect zero or placeholder tests without errors) and `npm run test`. Fix anything broken before building features.

---

## 6. Formal Regex Syntax (Must Follow Exactly)

| Construct | Syntax | Meaning |
|---|---|---|
| Symbol | any single character from the alphabet, e.g. `a`, `0` | matches that symbol |
| Union | `a\|b` (also accept `a+b` in "textbook mode") | either |
| Concatenation | `ab` (implicit) | sequence |
| Kleene star | `a*` | zero or more |
| Grouping | `( ... )` | precedence |
| Epsilon | `ε` (also accept `\e`) | empty string |
| Empty language | `∅` (also accept `\0`) | matches nothing |
| Escape | `\\|`, `\\*`, `\\(`, `\\)`, `\\\\` | literal operator characters |

**Precedence (highest to lowest):** star, concatenation, union.

**Optional sugar (desugared in the parser, shown to the user):** `a+` → `aa*`, `a?` → `(a|ε)`. Mark these as conveniences, not core operators.

**Explicitly unsupported (return a helpful error):** backreferences (`\1`), lookahead/lookbehind, lazy/possessive quantifiers, named groups, anchors as semantic operators. Explain that these go beyond classical regular languages.

The **alphabet** is inferred from the expression or set explicitly by the user. All DFA completion, complement, and equivalence operations must use an explicit alphabet.

---

## 7. Build Order (Phases)

Build in this order. Each phase ends with passing tests.

### Phase 1 — Regex Parser and AST (`engine/regex`)
- Lexer + recursive-descent parser producing an AST (`Symbol`, `Epsilon`, `Empty`, `Union`, `Concat`, `Star`).
- Pretty-printer (AST → canonical string) and parse-error reporting with position.
- Syntax-highlight token stream (for the editor).
- **Tests:** precedence, escapes, error cases, round-trip `parse(print(ast)) == ast`.

### Phase 2 — Automata Core (`engine/automata`)
- `NFA` (with ε-transitions) and `DFA` data classes; JSON serialization.
- **Thompson construction** (regex AST → ε-NFA) emitting steps.
- **Simulation** returning the full path: list of (state set, symbol, next state set) and accept/reject plus a reason for rejection (e.g. "no transition on `b` from {q2}", or "ended in non-accepting state").
- **Subset construction** (NFA → DFA) emitting the subset table as steps.
- **DFA completion** (add dead state) and **minimization** (Hopcroft or table-filling) emitting steps.
- Transition table generation.
- **Tests:** hand-checked small automata; every regex test string agrees between AST-based reference matcher, NFA, DFA, and minimized DFA.

### Phase 3 — Conversions (`engine/conversion`)
- **Automaton → regex** using **state elimination** (GNFA), with every elimination step recorded (which state removed, which new edge labels created). Also implement **Arden's theorem** method with equation-by-equation steps.
- Light **regex simplification** (e.g. `∅r → ∅`, `εr → r`, `r|∅ → r`, `(r*)* → r*`). Document that output is correct but not guaranteed minimal or human-readable.
- **Tests:** property-based (Hypothesis): random regex → NFA → regex → NFA must be language-equivalent (checked via Phase 5 equivalence once available, otherwise via exhaustive strings up to length N).

### Phase 4 — Grammar Converter (`engine/grammar`)
- Parse right-linear (and left-linear) regular grammars.
- Grammar ↔ NFA conversion and grammar ↔ regex via the NFA.
- **Derivation view:** show leftmost derivation for an accepted string, step by step.
- Detect and report non-regular (non-linear) grammars.
- **Tests:** round trips, derivations match simulation results.

### Phase 5 — Language Analyzer (`engine/analysis`)
- **Closure operations** on DFAs: union, intersection (product construction), complement, difference, concatenation, star, reversal.
- **Emptiness** and **finiteness** checks.
- **Equivalence** of two languages: build the symmetric difference DFA `(A \ B) ∪ (B \ A)`; if empty, they are equivalent; otherwise **BFS for the shortest accepted string** and return it as the distinguishing counterexample, stating which rule accepts it and which rejects it.
- **Subset / overlap / redundancy checks** between multiple rules (is rule A ⊆ rule B? do A and B overlap? provide a witness string).
- **Tests:** known equivalent pairs (`(a|b)*` vs `(a*b*)*`), known inequivalent pairs with verified counterexample, closure operations preserve language on shared test sets.

### Phase 6 — Backend API (`app/api`)
Expose the engine through FastAPI. Suggested endpoints:

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/regex/parse` | parse, return AST, tokens, errors |
| POST | `/api/regex/to-nfa` | regex → NFA (+ steps) |
| POST | `/api/automata/to-dfa` | NFA → DFA (+ subset table) |
| POST | `/api/automata/minimize` | DFA → minimal DFA (+ steps) |
| POST | `/api/automata/simulate` | automaton + string(s) → path(s) and verdicts |
| POST | `/api/automata/to-regex` | automaton → regex (+ elimination or Arden steps) |
| POST | `/api/grammar/convert` | grammar ↔ automaton/regex |
| POST | `/api/analysis/equivalence` | two rules → equal? + counterexample |
| POST | `/api/analysis/closure` | operation + operand rules → result automaton |
| POST | `/api/analysis/compare-many` | overlap/subset/redundancy matrix |
| POST | `/api/proofs/pumping/check` | validate a user's pumping-lemma step |
| GET/POST/PUT/DELETE | `/api/projects`, `/api/rules`, `/api/test-sets` | persistence |
| POST | `/api/automata/import` and GET `/api/automata/{id}/export` | JSON import/export |
| GET | `/api/reports/{id}/pdf` and `/csv` | report export |

Use Pydantic schemas. Return consistent error objects. **API tests** with `httpx` + FastAPI `TestClient`.

### Phase 7 — Frontend: Regex Studio (Must-have)
- Regex editor with **syntax highlighting** (token stream from the API or a local tokenizer) and inline error markers.
- **Live matching** against multiple test strings (list with accept/reject badges, optional expected-value column to flag mismatches).
- **NFA/DFA visualization** with React Flow: auto-layout, accepting states double-circled, start arrow, ε-edges visually distinct, parallel edges merged with combined labels.
- **Step-by-step simulation:** next/previous/play controls that highlight the current state(s) and edge, with a text explanation per step.
- **Transition table** with start/accepting indicators.
- Toggle between NFA, DFA, and minimized DFA views.
- Optional **visual regex builder** (blocks for union / concat / star / group) that produces the textual regex.

### Phase 8 — Frontend: Automata Lab (Must-have)
- Create and edit automata visually (add/remove states, set start/accepting, add labeled transitions including ε).
- Run NFA→DFA and DFA minimization with the **steps panel** showing each algorithm step.
- **Automaton → regex** with the state-elimination / Arden steps displayed.
- **Import/export** automata as JSON.

### Phase 9 — Frontend: Grammar Converter (Must-have)
- Grammar text editor with validation.
- Conversion to automaton and regex, plus derivation viewer for a chosen string.

### Phase 10 — Frontend: Language Analyzer (Must-have)
- Two-rule comparison screen: equivalent / not equivalent, with the **distinguishing string** and a replay of that string through both automata side by side.
- Closure operation builder (union, intersection, complement, difference, concatenation, star, reversal) with visual result.
- Overlap / subset / redundancy report across a set of rules.

### Phase 11 — Proof Workbench (Advanced)
Start small. **Do not attempt unrestricted theorem proving.**
- Provide **language templates** (e.g. `{aⁿbⁿ | n ≥ 0}`, `{ww | w ∈ {a,b}*}`, `{aⁿ | n is prime}`, `{a^(n²)}`, balanced parentheses).
- Guided **Pumping Lemma for regular languages** workflow: the user picks a pumping length *p*, a string *s* with |s| ≥ p, then every decomposition constraint `|xy| ≤ p`, `|y| ≥ 1` is enumerated, and the user selects an *i* that leaves the language. The checker validates each supported step.
- Always display: *"The Pumping Lemma can show that a language is not regular. Failing one pumping attempt does not prove non-regularity, and it can never prove a language is regular."*
- Clearly mark steps as **valid argument** vs **heuristic/example**.

### Phase 12 — Reports, Persistence, and Polish
- Save/load projects, rules, and test sets via the API.
- **PDF report** (rule definition, automaton diagrams, transition tables, equivalence verdict, counterexample, algorithm steps) and **CSV export** (test strings with verdicts, transition tables).
- Error handling, loading states, empty states, accessibility basics (keyboard navigation, contrast).
- Write a root `README.md` with setup and run commands.

---

## 8. Feature Checklist (Definition of Done)

**Core**
- [ ] Regex editor with syntax highlighting
- [ ] Live matching against multiple test strings
- [ ] NFA and DFA visualization
- [ ] Step-by-step input simulation with the transition path and rejection reasons
- [ ] Transition tables with accepting-state indicators
- [ ] Regex → automaton conversion
- [ ] Automaton → regex conversion with visible state-elimination or Arden steps
- [ ] Import and export of automata definitions (JSON)

**Modules**
- [ ] Regex Studio (must-have)
- [ ] Automata Lab (must-have)
- [ ] Grammar Converter (must-have)
- [ ] Language Analyzer: equivalence, closure operations, counterexamples (must-have)
- [ ] Proof Workbench: template-based guided Pumping Lemma (advanced)

**Objectives**
- [ ] Interactive environment for constructing and testing regexes
- [ ] Visual relationship between regex and finite automata
- [ ] Acceptance and rejection explained through state transitions
- [ ] Mathematical comparison of regular languages
- [ ] Identification of redundant, overlapping, or incorrect rules

**Quality**
- [ ] Every conversion/closure operation has a language-preservation test
- [ ] Property-based tests for regex → NFA → DFA → regex round trips
- [ ] Equivalence checker always returns a verified distinguishing string when languages differ
- [ ] Unsupported regex features produce clear errors
- [ ] Proof Workbench never claims testing proves regularity

---

## 9. Testing Requirements

**Backend (pytest + Hypothesis)**
- Unit tests per engine module in `backend/tests/engine/`.
- A shared fixture of test strings (all strings over the alphabet up to length 6, plus hand-picked edge cases) used by every conversion test.
- Core invariant tests: for any regex `r`, the AST reference matcher, NFA, DFA, minimized DFA, and `regex(automaton(r))` all accept exactly the same strings in the shared set. Strengthen with the equivalence checker.
- Closure tests: `L(A ∪ B) = L(A) ∪ L(B)`, `L(complement(A)) = Σ* \ L(A)`, etc., checked on the shared string set.
- API tests in `backend/tests/api/`.
- Target ≥ 90% coverage on `backend/engine`.

**Frontend (Vitest)**
- Component tests for the editor, test-string list, steps panel, and transition table.
- Tests for graph-layout helper functions and API client error handling.

**Commands**
```bash
cd backend && pytest --cov=engine
cd frontend && npm run test
```

---

## 10. Known Limitations (Show in the App's Help/About Page)

- Only classical regular languages are supported; features such as backreferences are intentionally excluded.
- Regexes produced by automaton → regex conversion are correct but not guaranteed simple or readable.
- The Pumping Lemma is a necessary condition for regularity. It cannot prove a language is regular, and a failed attempt does not prove non-regularity. The Proof Workbench distinguishes valid arguments from heuristics.
- The system explains its algorithms; it does not claim that AI can mathematically prove every user-submitted claim.

---

## 11. Working Instructions for the AI Assistant

1. Work phase by phase. Finish and test Phases 1–5 (the pure Python engine) **before** touching the API or UI.
2. Keep `engine/` free of FastAPI, database, or HTTP imports so it stays independently testable and demonstrable.
3. Every algorithm function returns `(result, steps)`, where `steps` is a list of serializable objects (`title`, `description`, optional `data`) defined in `engine/steps.py`.
4. Write the tests alongside each module, not afterward.
5. Prefer clear, well-commented code over clever code, since the algorithms must be explainable to an instructor.
6. After each phase, summarize what was built, what tests pass, and what comes next.
7. If something in this file conflicts with what is practical, pick the simplest option that preserves the Non-Negotiable Design Rules (Section 2) and note the decision in the README.
8. Run the app end to end at the end: backend on port 8000, frontend on port 3000, and walk through the demo flow below.

### Demo Flow (Final Acceptance Check)

1. Enter `(a|b)*abb` in Regex Studio and see the NFA and DFA.
2. Test `abb`, `aabb`, `ab`, `babb` and step through each path.
3. Convert the DFA back to a regex and view the elimination steps.
4. Compare `(a|b)*` with `(a*b*)*` and get "equivalent".
5. Compare `(a|b)*abb` with `(a|b)*ab` and get a verified distinguishing string.
6. Build a union of two rules in the Language Analyzer.
7. Convert a right-linear grammar to an automaton and show a derivation.
8. Walk through the Pumping Lemma template for `{aⁿbⁿ}`.
9. Export a PDF report and a CSV of test results.
