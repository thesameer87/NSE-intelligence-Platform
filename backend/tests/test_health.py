from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data

def test_metrics_stub() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "stub"
    assert "message" in data
