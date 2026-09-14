from pydantic import BaseModel
from langchain_ollama import ChatOllama
from graph.state import BizGPTState


class RecommendationPrioritizerOutput(BaseModel):
    high_priority_actions: list[str]
    medium_priority_actions: list[str]
    low_priority_actions: list[str]


llm = ChatOllama(model="phi3:mini")

llm_struct = llm.with_structured_output(
    RecommendationPrioritizerOutput
)


with open("prompts/recommendation_prioritizer.txt", "r") as f:
    prompt = f.read()


def recommendation_prioritizer(state: BizGPTState):

    print("entering recommendation priotizer")

    result = llm_struct.invoke(
        f"""
        {prompt}

        Recommendations:
        {state['recommendations']}

        Business Profile:
        {state['business_profile']}
        """
    )

    return {
        "prioritized_actions": result.model_dump()
    }