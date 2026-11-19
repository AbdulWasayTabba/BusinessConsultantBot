from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState


class MarketingOutput(BaseModel):
    seo_landscape: str
    social_media: str
    advertising_strategy: str
    customer_acquisition: str


llm = get_llm()
struct_llm = llm.with_structured_output(MarketingOutput)

with open("prompts/marketing_agent.txt") as f:
    prompt = f.read()


def marketing_agent(state: BizGPTState):
    result = struct_llm.invoke(
        f"""
        {prompt}
        
        Research Plan:
        {state['research_plan']}
        
        Business Profile:
        {state['business_profile']}
        """
    )

    return {"research_findings": [{"agent": "marketing", "findings": result.model_dump()}]}
