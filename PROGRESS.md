# Progress log
| Phase | Status | Notes |
|---|---|---|
| 0 | done | Added engine/app skeleton, shared errors and steps utilities, test configuration, environment examples, and smoke tests. Backend and frontend validation passed. |
| 1 | done | Implemented the formal regex AST, lexer, parser, printer, non-throwing highlighter, derivative matcher, and Hypothesis/reference tests. Backend tests, Ruff, and mypy passed. |
| 2 | done | Implemented validated NFA/DFA models, Thompson construction, simulation explanations, subset construction, epsilon removal/reversal, completion, minimization, transition tables, and language-preservation tests. 46 tests passed; Ruff and mypy passed. |
| 3 | done | Implemented regex simplification, GNFA state elimination, Arden conversion explanations, and the regex-to-automata pipeline. 54 tests passed; Ruff and mypy passed. |
| 4 | done | Implemented regular grammar parsing, printing, grammar/automaton/regex conversions, and cycle-safe derivation search. 63 tests passed; Ruff and mypy passed. |
| 5 | done | Implemented rule resolution, DFA alignment/products, closure operations, equivalence with shortest counterexamples, language properties, and multi-rule comparison. 68 tests passed; Ruff and mypy passed. |
| 6 | done | Implemented FastAPI engine endpoints, validation/error mapping, SQLAlchemy persistence models, CRUD routes, SQLite-testable API tests, and Alembic migration. 72 tests passed; Ruff and mypy passed. |
| 7 | done | Frontend foundation, API client, automaton views, helper utilities, placeholders, and `/studio` workflow. Frontend tests, lint, type-check, and production build pass. |
| 8 | done | Added the editable Automata Lab, pure automaton editing helpers, Zustand lab store, conversions, validation, import/export, simulation results, unsaved-work warning, and frontend tests. |
| 9 | done | Added the Grammar Converter UI with debounced parsing, grammar examples, grammar/automaton/regex conversions, derivation viewer, error line mapping, and frontend tests. |
| 10 | done | Added the tabbed Language Analyzer UI with reusable RuleEditor, equivalence checks, closure operations, properties, named rule comparisons, relation helpers, and analyzer tests. |
| 11 | done | Added the proof engine templates and pumping checks, proof API endpoints with limits, `/proofs` workbench, disclaimer, decomposition checker, numeric report, symbolic outlines, and backend/frontend tests. |
| 12 | done | Added PDF/CSV report exports, saved report regeneration, project switcher with project CRUD controls, Studio/Analyzer persistence actions, Help documentation, README setup instructions, responsive/accessibility polish, and final validation. Backend: 77 passed, engine coverage 90%, Ruff and mypy clean. Frontend: 9 test files/15 tests, lint, type-check, and build passed. PDF reports use tables/text rather than circular diagrams; full live browser walkthrough remains for manual review. |
