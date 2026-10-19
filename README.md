# RegexForge

RegexForge is an explainable toolkit for exploring classical regular languages. It parses restricted regular expressions and regular grammars, constructs and minimizes automata, compares languages, demonstrates Pumping Lemma arguments, and exports reports.

## Architecture

```
Next.js frontend (Studio, Lab, Grammar, Analyzer, Proofs)
              │ JSON/CSV/PDF over HTTP
FastAPI API ──┼── SQLAlchemy persistence
              │
Hand-written Python engine (regex → NFA → DFA → analysis/proofs)
              │
         PostgreSQL
```

## Setup for a new teammate

Prerequisites: Python 3.11+, Node 20+, Git, and PostgreSQL 15+.

```powershell
git clone <repository-url>
cd regexforce
createdb regexforge

cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
Copy-Item .env.example .env
# Edit .env with the PostgreSQL password and connection settings.
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open `http://localhost:3000`. The API documentation is at `http://localhost:8000/docs`.

Run all checks:

```powershell
cd backend
.venv\Scripts\python.exe -m pytest
.venv\Scripts\ruff.exe check .
.venv\Scripts\mypy.exe engine
cd ..\frontend
npm run test
npm run lint
npx tsc --noEmit
npm run build
```

The frontend package uses an `allowScripts` entry for the native resolver dependency in `package.json`; use the package manager's normal install flow and do not bypass scripts with `--force`.
