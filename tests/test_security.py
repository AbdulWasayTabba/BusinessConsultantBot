import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from api import main as api_main  # noqa: E402
from api import security  # noqa: E402
from tests.test_api import FakeWorkflow  # noqa: E402

BODY = {"message": "How do I grow my bakery?"}


@pytest.fixture
def client(monkeypatch):
    security.reset_rate_limits()
    monkeypatch.setattr(api_main, "get_workflow", lambda: FakeWorkflow())
    yield TestClient(api_main.app)
    security.reset_rate_limits()


def test_auth_disabled_when_no_keys(client, monkeypatch):
    monkeypatch.delenv("BIZGPT_API_KEYS", raising=False)
    assert client.post("/consult", json=BODY).status_code == 200


def test_rejects_missing_or_wrong_key(client, monkeypatch):
    monkeypatch.setenv("BIZGPT_API_KEYS", "secret1,secret2")
    assert client.post("/consult", json=BODY).status_code == 401
    bad = client.post("/consult", json=BODY, headers={"X-API-Key": "nope"})
    assert bad.status_code == 401
    ok = client.post("/consult", json=BODY, headers={"X-API-Key": "secret2"})
    assert ok.status_code == 200


def test_health_stays_public(client, monkeypatch):
    monkeypatch.setenv("BIZGPT_API_KEYS", "secret1")
    assert client.get("/health").status_code == 200


def test_rate_limit_returns_429(client, monkeypatch):
    monkeypatch.delenv("BIZGPT_API_KEYS", raising=False)
    monkeypatch.setenv("BIZGPT_RATE_LIMIT", "2")
    assert client.post("/consult", json=BODY).status_code == 200
    assert client.post("/consult", json=BODY).status_code == 200
    resp = client.post("/consult", json=BODY)
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers
