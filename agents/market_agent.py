from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState


class MarketOutput(BaseModel):
    industry_trends: list[str]
    market_size: str
    customer_behavior: str
    demand_shifts: str


llm = get_llm()
struct_llm = llm.with_structured_output(MarketOutput)

with open("prompts/market_agent.txt") as f:
    prompt_text = f.read()


def market_agent(state: BizGPTState):
    result = struct_llm.invoke(
        f"""
        {prompt_text}

        Business Profile:
        {state['business_profile']}

        Research Plan:
        {state['research_plan']}
        """
    )

    return {"research_findings": [{"agent": "market", "findings": result.model_dump()}]}
