from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState


class CustomerOutput(BaseModel):
    customer_reviews: str
    pain_points: list[str]
    satisfaction: str
    retention: str


llm = get_llm()
struct_llm = llm.with_structured_output(CustomerOutput)

with open("prompts/customer_agent.txt") as f:
    prompt = f.read()


def customer_agent(state: BizGPTState):
    result = struct_llm.invoke(
        f"""
        {prompt}
        
        Research Plan:
        {state['research_plan']}
        
        Business Profile:
        {state['business_profile']}
        """
    )

    return {"research_findings": [{"agent": "customer", "findings": result.model_dump()}]}
