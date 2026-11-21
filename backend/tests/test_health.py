from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_api_process_only() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pixmail-api"}


def test_api_status_does_not_claim_database_connection() -> None:
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json()["database"] == "not_connected"
