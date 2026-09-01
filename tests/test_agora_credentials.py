from app import create_app
from app.config import Settings


def test_returns_scoped_agora_credentials():
    app = create_app(Settings(agora_app_id="app-id", agora_temp_token="token"))
    response = app.test_client().post(
        "/api/v1/realtime/agora/credentials",
        json={"channel": "lesson_123", "uid": 42, "role": "publisher"},
    )
    assert response.status_code == 200
    assert response.json["app_id"] == "app-id"
    assert response.json["channel"] == "lesson_123"
    assert response.json["uid"] == 42


def test_rejects_unsafe_channel_name():
    app = create_app(Settings(agora_app_id="app-id"))
    response = app.test_client().post(
        "/api/v1/realtime/agora/credentials", json={"channel": "../other", "uid": 42}
    )
    assert response.status_code == 400


def test_reports_missing_agora_configuration():
    app = create_app(Settings())
    response = app.test_client().post(
        "/api/v1/realtime/agora/credentials", json={"channel": "lesson_123", "uid": 42}
    )
    assert response.status_code == 503

