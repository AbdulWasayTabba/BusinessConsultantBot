"""FastAPI REST interface for the BizGPT consultant graph.

Run with: ``uvicorn api.main:app --host 0.0.0.0 --port 8000``
"""

from __future__ import annotations

import uuid
from functools import lru_cache
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="BizGPT Business Consultant API", version="0.1.0")


class ConsultRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or clarification answer")
    thread_id: str | None = Field(None, description="Conversation id; omit to start a new one")


class ConsultResponse(BaseModel):
    thread_id: str
    status: Literal["needs_clarification", "completed"]
    question: str | None = None
    report: str | None = None


@lru_cache(maxsize=1)
def get_workflow():
    """Import the compiled graph lazily so /health stays cheap and tests can stub it."""
    from graph.graph import workflow

    return workflow


def _pending_question(workflow: Any, config: dict) -> str | None:
    snapshot = workflow.get_state(config)
    for task in getattr(snapshot, "tasks", None) or []:
        if task.interrupts:
            value = getattr(task.interrupts[0], "value", task.interrupts[0])
            if isinstance(value, dict):
                return str(value.get("question") or value)
            return str(value)
    return None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/consult", response_model=ConsultResponse)
def consult(req: ConsultRequest) -> ConsultResponse:
    workflow = get_workflow()
    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        if req.thread_id and _pending_question(workflow, config):
            from langgraph.types import Command

            workflow.invoke(Command(resume=req.message), config=config)
        else:
            initial_state = {
                "user_input": req.message,
                "research_findings": [],
                "replan_count": 0,
                "clarification_attempts": 0,
            }
            workflow.invoke(initial_state, config=config)

        question = _pending_question(workflow, config)
        if question:
            return ConsultResponse(
                thread_id=thread_id, status="needs_clarification", question=question
            )

        values = workflow.get_state(config).values or {}
    except Exception as exc:  # surface graph/LLM failures as a clean 502
        raise HTTPException(status_code=502, detail=f"Consultation failed: {exc}") from exc

    report = (
        values.get("final_report")
        or values.get("final_response")
        or values.get("report")
        or "No report generated."
    )
    return ConsultResponse(thread_id=thread_id, status="completed", report=str(report))
