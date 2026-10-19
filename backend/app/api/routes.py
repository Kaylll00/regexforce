"""FastAPI routes for engine operations and persistence."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AnalysisReport, Project, Rule, TestSet
from app.db.session import get_db
from app.schemas.api import (
    AutomatonRequest,
    GrammarRequest,
    ProjectInput,
    RegexRequest,
    RuleInput,
    RuleRequest,
    SimulateRequest,
    TestSetInput,
)
from app.services.engine_service import (
    automaton_result,
    build_regex,
    get_automaton,
    parse_regex,
    steps_result,
)
from engine.analysis.closure import apply_closure
from engine.analysis.equivalence import check_equivalence
from engine.analysis.properties import is_empty, is_finite, is_universal, shortest_accepted
from engine.analysis.rules import resolve_rule
from engine.analysis.rules_set import compare_many
from engine.automata.dfa_ops import complete_dfa, minimize_dfa
from engine.automata.model import NFA
from engine.automata.nfa_ops import dfa_to_nfa
from engine.automata.simulate import simulate
from engine.automata.subset import nfa_to_dfa
from engine.conversion.arden import automaton_to_regex_arden
from engine.conversion.state_elimination import automaton_to_regex_state_elimination
from engine.grammar.convert import (
    grammar_to_nfa,
    grammar_to_regex,
    nfa_to_grammar,
    regex_to_grammar,
)
from engine.grammar.derivation import find_derivation
from engine.grammar.parser import parse_grammar
from engine.grammar.printer import grammar_to_text
from engine.regex.parser import parse
from engine.regex.printer import to_string

router = APIRouter(prefix="/api")


@router.post("/regex/parse")
def regex_parse(request: RegexRequest):
    return parse_regex(request.regex, request.textbook)


@router.post("/regex/build")
def regex_build(request: RegexRequest):
    return build_regex(request.regex, request.textbook, request.alphabet)


@router.post("/automata/validate")
def automata_validate(request: AutomatonRequest):
    return automaton_result(get_automaton(request.automaton))


@router.post("/automata/simulate")
def automata_simulate(request: SimulateRequest):
    automaton = get_automaton(request.automaton)
    return {"results": [
        {
            "string": value,
            "accepted": result.accepted,
            "steps": [step.__dict__ for step in result.steps],
            "reason": result.reason,
            "rejected_at": result.rejected_at,
        }
        for value in request.strings
        for result in [simulate(automaton, value)]
    ]}


@router.post("/automata/to-dfa")
def automata_to_dfa(request: AutomatonRequest):
    automaton = get_automaton(request.automaton)
    dfa, steps = nfa_to_dfa(automaton if isinstance(automaton, NFA) else dfa_to_nfa(automaton))
    return steps_result(dfa, steps)


@router.post("/automata/complete")
def automata_complete(request: AutomatonRequest):
    automaton = get_automaton(request.automaton)
    if isinstance(automaton, NFA):
        automaton, _ = nfa_to_dfa(automaton)
    result, steps = complete_dfa(automaton)
    return steps_result(result, steps)


@router.post("/automata/minimize")
def automata_minimize(request: AutomatonRequest):
    automaton = get_automaton(request.automaton)
    if isinstance(automaton, NFA):
        automaton, _ = nfa_to_dfa(automaton)
    result, steps = minimize_dfa(automaton, False)
    return steps_result(result, steps)


@router.post("/automata/to-regex")
def automata_to_regex(request: dict[str, Any]):
    automaton = get_automaton(request["automaton"])
    node, steps = (
        automaton_to_regex_arden(automaton)
        if request.get("method") == "arden"
        else automaton_to_regex_state_elimination(automaton)
    )
    return {"regex": to_string(node), "steps": [step.to_dict() for step in steps]}


@router.post("/grammar/parse")
def grammar_parse(request: GrammarRequest):
    grammar, steps = parse_grammar(request.grammar)
    return {
        "kind": grammar.kind,
        "productions": [{"head": p.head, "body": list(p.body)} for p in grammar.productions],
        "canonical": request.grammar,
        "steps": [step.to_dict() for step in steps],
    }


@router.post("/grammar/to-automaton")
def grammar_to_automaton_endpoint(request: GrammarRequest):
    grammar, parse_steps = parse_grammar(request.grammar)
    nfa, grammar_steps = grammar_to_nfa(grammar)
    dfa, dfa_steps = nfa_to_dfa(nfa)
    return {
        "nfa": nfa.to_dict(), "dfa": dfa.to_dict(),
        "tables": {"nfa": automaton_result(nfa)["table"], "dfa": automaton_result(dfa)["table"]},
        "steps": [step.to_dict() for step in [*parse_steps, *grammar_steps, *dfa_steps]],
    }


@router.post("/grammar/to-regex")
def grammar_to_regex_endpoint(request: GrammarRequest):
    grammar, parse_steps = parse_grammar(request.grammar)
    node, steps = grammar_to_regex(grammar)
    return {"regex": to_string(node), "steps": [step.to_dict() for step in [*parse_steps, *steps]]}


@router.post("/grammar/from-regex")
def grammar_from_regex(request: RegexRequest):
    node, parse_steps = parse(request.regex, textbook=request.textbook)
    grammar, steps = regex_to_grammar(node)
    return {"grammar": grammar_to_text(grammar), "steps": [step.to_dict() for step in [*parse_steps, *steps]]}


@router.post("/grammar/from-automaton")
def grammar_from_automaton(request: AutomatonRequest):
    grammar, steps = nfa_to_grammar(get_automaton(request.automaton))
    return {"grammar": grammar_to_text(grammar), "steps": [step.to_dict() for step in steps]}


@router.post("/grammar/derive")
def grammar_derive(request: dict[str, str]):
    grammar, parse_steps = parse_grammar(request["grammar"])
    forms, steps = find_derivation(grammar, request["string"])
    return {"accepted": forms is not None, "forms": forms, "steps": [step.to_dict() for step in [*parse_steps, *steps]]}


@router.post("/analysis/equivalence")
def analysis_equivalence(request: dict[str, Any]):
    a, a_steps = resolve_rule(request["a"], request.get("alphabet"))
    b, b_steps = resolve_rule(request["b"], request.get("alphabet"))
    result = check_equivalence(a, b)
    return {
        "equivalent": result.equivalent, "counterexample": result.counterexample,
        "a_accepts": result.a_accepts, "b_accepts": result.b_accepts,
        "steps": [step.to_dict() for step in [*a_steps, *b_steps, *result.steps]],
    }


@router.post("/analysis/closure")
def analysis_closure(request: dict[str, Any]):
    operands = [resolve_rule(rule, request.get("alphabet"))[0] for rule in request["operands"]]
    result, steps = apply_closure(request["operation"], operands, request.get("minimize", True))
    return steps_result(result, steps)


@router.post("/analysis/properties")
def analysis_properties(request: RuleRequest):
    dfa, _ = resolve_rule(request.rule, request.alphabet)
    return {
        "empty": is_empty(dfa), "finite": is_finite(dfa), "universal": is_universal(dfa),
        "shortest_accepted": shortest_accepted(dfa),
    }


@router.post("/analysis/compare-many")
def analysis_compare_many(request: dict[str, Any]):
    rules = [(item["name"], resolve_rule(item["rule"], request.get("alphabet"))[0]) for item in request["rules"]]
    report = compare_many(rules)
    return {"matrix": report.matrix, "redundant": report.redundant}


@router.post("/projects")
def create_project(request: ProjectInput, db: Session = Depends(get_db)):
    project = Project(name=request.name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "name": project.name}


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return [{"id": project.id, "name": project.name} for project in db.scalars(select(Project)).all()]


@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return {"id": project.id, "name": project.name}


@router.put("/projects/{project_id}")
def update_project(project_id: int, request: ProjectInput, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    project.name = request.name
    db.commit()
    return {"id": project.id, "name": project.name}


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    db.commit()
    return {"deleted": True}


@router.post("/projects/{project_id}/rules")
def create_rule(project_id: int, request: RuleInput, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "Project not found")
    item = Rule(project_id=project_id, name=request.name, kind=request.kind, definition=request.definition)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "project_id": item.project_id, "name": item.name, "kind": item.kind, "definition": item.definition}


@router.get("/projects/{project_id}/rules")
def list_rules(project_id: int, db: Session = Depends(get_db)):
    return [
        {"id": item.id, "project_id": item.project_id, "name": item.name, "kind": item.kind, "definition": item.definition}
        for item in db.scalars(select(Rule).where(Rule.project_id == project_id)).all()
    ]


@router.put("/rules/{rule_id}")
def update_rule(rule_id: int, request: RuleInput, db: Session = Depends(get_db)):
    item = db.get(Rule, rule_id)
    if item is None:
        raise HTTPException(404, "Rule not found")
    item.name, item.kind, item.definition = request.name, request.kind, request.definition
    db.commit()
    return {"id": item.id, "project_id": item.project_id, "name": item.name, "kind": item.kind, "definition": item.definition}


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    item = db.get(Rule, rule_id)
    if item is None:
        raise HTTPException(404, "Rule not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.post("/projects/{project_id}/test-sets")
def create_test_set(project_id: int, request: TestSetInput, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "Project not found")
    item = TestSet(project_id=project_id, name=request.name, strings=request.strings)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "project_id": item.project_id, "name": item.name, "strings": item.strings}


@router.get("/projects/{project_id}/test-sets")
def list_test_sets(project_id: int, db: Session = Depends(get_db)):
    return [
        {"id": item.id, "project_id": item.project_id, "name": item.name, "strings": item.strings}
        for item in db.scalars(select(TestSet).where(TestSet.project_id == project_id)).all()
    ]


@router.put("/test-sets/{test_set_id}")
def update_test_set(test_set_id: int, request: TestSetInput, db: Session = Depends(get_db)):
    item = db.get(TestSet, test_set_id)
    if item is None:
        raise HTTPException(404, "Test set not found")
    item.name, item.strings = request.name, request.strings
    db.commit()
    return {"id": item.id, "project_id": item.project_id, "name": item.name, "strings": item.strings}


@router.delete("/test-sets/{test_set_id}")
def delete_test_set(test_set_id: int, db: Session = Depends(get_db)):
    item = db.get(TestSet, test_set_id)
    if item is None:
        raise HTTPException(404, "Test set not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.post("/projects/{project_id}/reports")
def create_report(project_id: int, request: dict[str, Any], db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "Project not found")
    item = AnalysisReport(
        project_id=project_id,
        kind=request.get("kind", "analysis"),
        input_refs=request.get("input_refs", {}),
        result=request.get("result", {}),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "project_id": project_id, "kind": item.kind, "result": item.result}
