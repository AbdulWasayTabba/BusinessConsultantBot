from pydantic import BaseModel
from config import get_llm, get_settings

from graph.state import BizGPTState


class JudgeOutput(BaseModel):
    evidence_coverage: str
    reasoning_quality: str
    missing_information: list[str]
    research_needed: bool


llm = get_llm(get_settings().judge_model)

llm_struct = llm.with_structured_output(JudgeOutput)

with open("prompts/judge_agent.txt", "r") as f:
    prompt = f.read()


def judge_agent(state: BizGPTState):
    print("entering judge agent")
    result = llm_struct.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Diagnosis:
        {state['diagnosis']}

        Research Findings:
        {state['research_findings']}

        Synthesized Insights:
        {state['synthesized_insights']}

        Recommendations:
        {state['recommendations']}
        """
    )

    return {
        "judge_feedback": result.model_dump()
    }