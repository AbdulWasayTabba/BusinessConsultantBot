from pydantic import BaseModel
from langchain_ollama import ChatOllama
from graph.state import BizGPTState


class RiskChangeReviewerOutput(BaseModel):
    implementation_risks: list[str]
    mitigation_strategies: list[str]
    change_management_considerations: list[str]


llm = ChatOllama(model="phi3:mini")

llm_struct = llm.with_structured_output(
    RiskChangeReviewerOutput
)


with open("prompts/risk_change_reviewer.txt", "r") as f:
    prompt = f.read()


def risk_change_reviewer(state: BizGPTState):
    print("entering risk change reviewer")
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

    return {
        "risk_review": result.model_dump()
    }