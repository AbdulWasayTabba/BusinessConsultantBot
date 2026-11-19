from pydantic import BaseModel

from config import get_llm, get_settings
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class PlannerOutput(BaseModel):
    research_tasks: list[str]


llm = get_llm(get_settings().consultant_model, streaming=True)
struct_llm = llm.with_structured_output(PlannerOutput)


with open("prompts/planner.txt") as f:
    prompt = f.read()


def planner(state: BizGPTState):
    logger.info("node_enter", extra={"node": "planner"})

    result = struct_llm.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Diagnosis:
        {state['diagnosis']}

        Problem Categories:
        {state['problem_categories']}

        User Input:
        {state['user_input']}
        """
    )

    return {"research_plan": result.research_tasks}
