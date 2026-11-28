from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class RiskChangeReviewerOutput(BaseModel):
    implementation_risks: list[str]
    mitigation_strategies: list[str]
    change_management_considerations: list[str]


llm = get_llm()

llm_struct = llm.with_structured_output(RiskChangeReviewerOutput)


with open("prompts/risk_change_reviewer.txt") as f:
    prompt = f.read()


def risk_change_reviewer(state: BizGPTState) -> dict:
    logger.info("node_enter", extra={"node": "risk_change_reviewer"})
    result = llm_struct.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Prioritized Actions:
        {state['prioritized_actions']}

        Implementation Plan:
        {state['implementation_plan']}
        """
    )

    return {"risk_review": result.model_dump()}
