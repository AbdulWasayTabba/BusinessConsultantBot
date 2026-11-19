from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class RecommendationPrioritizerOutput(BaseModel):
    high_priority_actions: list[str]
    medium_priority_actions: list[str]
    low_priority_actions: list[str]


llm = get_llm()

llm_struct = llm.with_structured_output(RecommendationPrioritizerOutput)


with open("prompts/recommendation_prioritizer.txt") as f:
    prompt = f.read()


def recommendation_prioritizer(state: BizGPTState):
    logger.info("node_enter", extra={"node": "recommendation_prioritizer"})

    result = llm_struct.invoke(
        f"""
        {prompt}

        Recommendations:
        {state['recommendations']}

        Business Profile:
        {state['business_profile']}
        """
    )

    return {"prioritized_actions": result.model_dump()}
