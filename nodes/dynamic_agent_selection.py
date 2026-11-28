from typing import Literal

from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class DynamicAgentSelectionOutput(BaseModel):
    selected_agents: list[
        Literal[
            "market_agent",
            "competitor_agent",
            "marketing_agent",
            "operations_agent",
            "finance_agent",
            "customer_agent",
        ]
    ]


llm = get_llm()

struct_llm = llm.with_structured_output(DynamicAgentSelectionOutput)

with open("prompts/dynamic_agent_selection.txt") as f:
    prompt = f.read()


def dynamic_agent_selection(state: BizGPTState) -> dict:
    logger.info("node_enter", extra={"node": "dynamic_agent_selection"})

    result = struct_llm.invoke(
        f"""
        {prompt}

        Research Plan:
        {state['research_plan']}

        Problem Categories:
        {state['problem_categories']}

        Diagnosis:
        {state['diagnosis']}
        """
    )

    return {"selected_agents": result.selected_agents}
