from typing import Literal

from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class IntentRouterOutput(BaseModel):
    route_type: Literal[
        "greeting", "business_qa", "report_revision", "follow_up_q", "business_analysis", "invalid"
    ]


llm = get_llm()
structured_llm = llm.with_structured_output(IntentRouterOutput)

with open("prompts/intent_router.txt") as f:
    prompt = f.read()


def intent_router(state: BizGPTState):
    logger.info("node_enter", extra={"node": "intent_router"})
    result = structured_llm.invoke(f"{prompt}\n\nUser Input:\n{state.get('user_input', '')}")
    return {"route_type": result.route_type}
