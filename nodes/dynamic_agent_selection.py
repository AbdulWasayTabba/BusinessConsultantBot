from graph.state import BizGPTState
from typing import Literal
from pydantic import BaseModel
from langchain_ollama import ChatOllama


class DynamicAgentSelectionOutput(BaseModel):
    selected_agents: list[
        Literal[
            "market_agent",
            "competitor_agent",
            "marketing_agent",
            "operations_agent",
            "finance_agent",
            "customer_agent"
        ]
    ]


llm = ChatOllama(model="phi3:mini")

struct_llm = llm.with_structured_output(
    DynamicAgentSelectionOutput
)

with open("prompts/dynamic_agent_selection.txt", "r") as f:
    prompt = f.read()


def dynamic_agent_selection(state: BizGPTState):
    print("dynamic agent")

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

    return {
        "selected_agents": result.selected_agents
    }