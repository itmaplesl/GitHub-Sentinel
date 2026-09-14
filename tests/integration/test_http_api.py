from fastapi.testclient import TestClient

from github_sentinel.config import Settings
from github_sentinel.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app(Settings()))

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_subscription_crud_skeleton() -> None:
    client = TestClient(create_app(Settings(api_key="secret")))
    headers = {"X-API-Key": "secret"}

    created = client.post(
        "/api/v1/subscriptions",
        headers=headers,
        json={
            "repository": "openai/openai-python",
            "schedule_type": "daily",
            "timezone": "Asia/Shanghai",
            "event_types": ["release", "pull_request"],
            "notification_channels": [],
        },
    )

    assert created.status_code == 201
    subscription_id = created.json()["id"]
    listed = client.get("/api/v1/subscriptions", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == subscription_id

    deleted = client.delete(f"/api/v1/subscriptions/{subscription_id}", headers=headers)
    assert deleted.status_code == 204


def test_api_key_is_enforced_when_configured() -> None:
    client = TestClient(create_app(Settings(api_key="secret")))

    response = client.get("/api/v1/subscriptions")

    assert response.status_code == 401
