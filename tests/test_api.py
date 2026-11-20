from types import SimpleNamespace

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from api import main as api_main  # noqa: E402


class FakeWorkflow:
    def __init__(self, interrupt_first=False):
        self.interrupt = interrupt_first
        self.calls = []

    def invoke(self, payload, config):
        self.calls.append(payload)
        if not isinstance(payload, dict):
            self.interrupt = False

    def get_state(self, config):
        if self.interrupt:
            task = SimpleNamespace(interrupts=[SimpleNamespace(value={"question": "Budget?"})])
            return SimpleNamespace(tasks=[task], values={})
        return SimpleNamespace(tasks=[], values={"final_report": "Do X"})


@pytest.fixture
def client(monkeypatch):
    fake = FakeWorkflow(interrupt_first=True)
    monkeypatch.setattr(api_main, "get_workflow", lambda: fake)
    return TestClient(api_main.app), fake


def test_health():
    assert TestClient(api_main.app).get("/health").json() == {"status": "ok"}


def test_consult_clarification_then_resume(client):
    c, fake = client
    r = c.post("/consult", json={"message": "Grow my bakery"}).json()
    assert r["status"] == "needs_clarification" and r["question"] == "Budget?"
    r2 = c.post("/consult", json={"message": "$5k", "thread_id": r["thread_id"]}).json()
    assert r2 == {
        "thread_id": r["thread_id"],
        "status": "completed",
        "question": None,
        "report": "Do X",
    }


def test_consult_rejects_empty_message(client):
    c, _ = client
    assert c.post("/consult", json={"message": ""}).status_code == 422
