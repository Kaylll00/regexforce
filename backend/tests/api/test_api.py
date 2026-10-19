import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_regex_build_contract(client) -> None:
    response = client.post("/api/regex/build", json={"regex": "(a|b)*abb"})
    assert response.status_code == 200
    assert len(response.json()["min_dfa"]["states"]) == 4


def test_engine_error_shape(client) -> None:
    response = client.post("/api/regex/parse", json={"regex": "a|"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "regex_syntax"
    assert response.json()["error"]["position"] == 1


def test_automata_simulation_endpoint(client) -> None:
    built = client.post("/api/regex/build", json={"regex": "a"}).json()
    response = client.post(
        "/api/automata/simulate",
        json={"automaton": built["min_dfa"], "strings": ["a", "b"]},
    )
    assert response.status_code == 200
    assert [item["accepted"] for item in response.json()["results"]] == [True, False]


def test_project_crud_and_cascade(client) -> None:
    project = client.post("/api/projects", json={"name": "Demo"}).json()
    project_id = project["id"]
    created = client.post(
        f"/api/projects/{project_id}/rules",
        json={"name": "rule", "kind": "regex", "definition": {"regex": "a"}},
    )
    assert created.status_code == 200
    assert client.get(f"/api/projects/{project_id}/rules").json()[0]["name"] == "rule"
    assert client.delete(f"/api/projects/{project_id}").json() == {"deleted": True}
    assert client.get(f"/api/projects/{project_id}").status_code == 404
