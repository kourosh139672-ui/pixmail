from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_api_process_only() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pixmail-api"}


def test_status_reports_auth_configuration_without_claiming_database_connection() -> None:
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "prototype"
    assert body["database"] == "not_connected"
    assert body["authentication"] in {"configured", "not_configured"}
    assert body["username_login"] in {"configured", "needs_server_secret_key"}


def test_register_rejects_username_with_symbols() -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "bad_name!",
            "recovery_email": "person@example.com",
            "password": "a-long-safe-password",
        },
    )
    assert response.status_code == 422


def test_login_rejects_invalid_username_format() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "bad name", "password": "password"},
    )
    assert response.status_code == 422


def test_recovery_does_not_accept_invalid_username() -> None:
    response = client.post(
        "/api/v1/auth/recover",
        json={"username": "x"},
    )
    assert response.status_code == 422
