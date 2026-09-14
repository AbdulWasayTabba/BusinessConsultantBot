from graph.state import BizGPTState
from langchain_ollama import ChatOllama
from pydantic import BaseModel


class FinanceOutput(BaseModel):
    revenue_analysis: list[str]
    cost_structure: list[str]
    profitability_insights: list[str]
    pricing_observations: list[str]
    financial_risks: list[str]


llm = ChatOllama(model="phi3:mini")
struct_llm = llm.with_structured_output(FinanceOutput)

with open("prompts/finance_agent.txt", "r") as f:
    prompt_text = f.read()


def finance_agent(state: BizGPTState):
    result = struct_llm.invoke(
        f"""
        {prompt_text}

        Business Profile:
        {state['business_profile']}

        Research Plan:
        {state['research_plan']}
        """
    )

    return {
        "research_findings": [
            {
                "agent": "finance",
                "findings": result.model_dump()
            }
        ]
    }