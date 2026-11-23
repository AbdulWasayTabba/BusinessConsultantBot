"""FastAPI REST interface for the BizGPT consultant graph.

Run with: ``uvicorn api.main:app --host 0.0.0.0 --port 8000``
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from functools import lru_cache
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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


def _graph_input(workflow: Any, req: ConsultRequest, config: dict) -> Any:
    """Resume a paused thread with the user's answer, or build a fresh initial state."""
    if req.thread_id and _pending_question(workflow, config):
        from langgraph.types import Command

        return Command(resume=req.message)
    return {
        "user_input": req.message,
        "research_findings": [],
        "replan_count": 0,
        "clarification_attempts": 0,
    }


def _final_report(values: dict) -> str:
    return str(
        values.get("final_report")
        or values.get("final_response")
        or values.get("report")
        or "No report generated."
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/consult", response_model=ConsultResponse)
def consult(req: ConsultRequest) -> ConsultResponse:
    workflow = get_workflow()
    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        workflow.invoke(_graph_input(workflow, req, config), config=config)

        question = _pending_question(workflow, config)
        if question:
            return ConsultResponse(
                thread_id=thread_id, status="needs_clarification", question=question
            )

        values = workflow.get_state(config).values or {}
    except Exception as exc:  # surface graph/LLM failures as a clean 502
        raise HTTPException(status_code=502, detail=f"Consultation failed: {exc}") from exc

    return ConsultResponse(thread_id=thread_id, status="completed", report=_final_report(values))


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@app.post("/consult/stream")
def consult_stream(req: ConsultRequest) -> StreamingResponse:
    """Server-Sent Events version of /consult.

    Emits ``node`` events as each graph node finishes, then a terminal ``clarification``,
    ``completed`` or ``error`` event carrying the same fields as ``ConsultResponse``.
    """
    workflow = get_workflow()
    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    def events() -> Iterator[str]:
        yield _sse("start", {"thread_id": thread_id})
        try:
            payload = _graph_input(workflow, req, config)
            for update in workflow.stream(payload, config=config, stream_mode="updates"):
                for node in update or {}:
                    if node != "__interrupt__":
                        yield _sse("node", {"thread_id": thread_id, "node": node})
            question = _pending_question(workflow, config)
            if question:
                yield _sse(
                    "clarification",
                    {"thread_id": thread_id, "status": "needs_clarification", "question": question},
                )
                return
            values = workflow.get_state(config).values or {}
            yield _sse(
                "completed",
                {"thread_id": thread_id, "status": "completed", "report": _final_report(values)},
            )
        except Exception as exc:  # stream already started: report failure in-band
            yield _sse("error", {"thread_id": thread_id, "detail": f"Consultation failed: {exc}"})

    return StreamingResponse(events(), media_type="text/event-stream")
