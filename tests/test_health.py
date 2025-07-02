"""Basic health-check test for the FastAPI backend."""
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_health_check() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"
