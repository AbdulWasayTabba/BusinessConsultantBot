"""Checkpointer factory for conversation/session persistence.

Selection (env var ``BIZGPT_CHECKPOINT_DB``):
- unset / empty / ``memory`` -> in-process ``MemorySaver`` (default; lost on restart)
- a file path, e.g. ``data/checkpoints.sqlite`` -> ``SqliteSaver`` (survives restarts)

Falls back to ``MemorySaver`` with a warning if ``langgraph-checkpoint-sqlite`` is not
installed. A Postgres backend can be added here later behind the same function.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

ENV_VAR = "BIZGPT_CHECKPOINT_DB"


def get_checkpointer(db_path: str | None = None):
    """Return a LangGraph checkpointer based on ``db_path`` or ``BIZGPT_CHECKPOINT_DB``."""
    target = (db_path if db_path is not None else os.getenv(ENV_VAR, "")).strip()
    if not target or target.lower() == "memory":
        return MemorySaver()
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        logger.warning(
            "%s=%s set but langgraph-checkpoint-sqlite is not installed; using MemorySaver",
            ENV_VAR,
            target,
        )
        return MemorySaver()
    if target != ":memory:":
        Path(target).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target, check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()
    return saver
