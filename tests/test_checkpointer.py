import pytest

pytest.importorskip("langgraph")

from langgraph.checkpoint.memory import MemorySaver  # noqa: E402

from graph.checkpointer import get_checkpointer  # noqa: E402


def test_default_is_memory(monkeypatch):
    monkeypatch.delenv("BIZGPT_CHECKPOINT_DB", raising=False)
    assert isinstance(get_checkpointer(), MemorySaver)


def test_memory_keyword():
    assert isinstance(get_checkpointer("memory"), MemorySaver)


def test_sqlite_path(tmp_path):
    sqlite_mod = pytest.importorskip("langgraph.checkpoint.sqlite")
    saver = get_checkpointer(str(tmp_path / "sub" / "cp.sqlite"))
    assert isinstance(saver, sqlite_mod.SqliteSaver)
    assert (tmp_path / "sub" / "cp.sqlite").exists()
