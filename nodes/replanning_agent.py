from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class ReplanningOutput(BaseModel):
    updated_research_plan: list[str]
    recommended_agents: list[str]


llm = get_llm()

llm_struct = llm.with_structured_output(ReplanningOutput)


with open("prompts/replanning_agent.txt") as f:
    prompt = f.read()


def replanning_agent(state: BizGPTState):
    logger.info("node_enter", extra={"node": "replanning_agent"})
    result = llm_struct.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Diagnosis:
        {state['diagnosis']}

        Research Findings:
        {state['research_findings']}

        Research Gaps:
        {state['research_gaps']}

        Judge Feedback:
        {state['judge_feedback']}
        """
    )

    return {
        "research_plan": result.updated_research_plan,
        "selected_agents": result.recommended_agents,
        "replan_count": state.get("replan_count", 0) + 1,
    }
