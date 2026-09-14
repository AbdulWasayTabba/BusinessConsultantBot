from pydantic import BaseModel
from langchain_ollama import ChatOllama
from graph.state import BizGPTState


class ImplementationPlannerOutput(BaseModel):
    action_plan: list[str]
    timeline: list[str]
    resources_required: list[str]
    dependencies: list[str]


llm = ChatOllama(model="phi3:mini")

llm_struct = llm.with_structured_output(
    ImplementationPlannerOutput
)

with open("prompts/implementation_planner.txt", "r") as f:
    prompt = f.read()


def implementation_planner(state: BizGPTState):
    print("entering implementation planner")

    result = llm_struct.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Prioritized Actions:
        {state['prioritized_actions']}
        """
    )

    return {
        "implementation_plan": result.model_dump()
    }