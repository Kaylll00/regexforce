from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_pdf_and_csv_exports():
    pdf = client.post("/api/reports/pdf", json={"title": "Test", "regex": "a*", "strings": []})
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    csv = client.post("/api/reports/csv", json={"kind": "tests", "strings": [{"value": "a", "actual": True}]})
    assert csv.status_code == 200
    assert "string,expected,actual,match" in csv.text
