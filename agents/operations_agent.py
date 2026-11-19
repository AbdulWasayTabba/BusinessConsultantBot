from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState


class OperationsOutput(BaseModel):
    processes: str
    staffing: str
    inventory: str
    efficiency: str


llm = get_llm()
struct_llm = llm.with_structured_output(OperationsOutput)

with open("prompts/operations_agent.txt") as f:
    prompt = f.read()


def operations_agent(state: BizGPTState):
    result = struct_llm.invoke(
        f"""
        {prompt}
        
        Research Plan:
        {state['research_plan']}
        
        Business Profile:
        {state['business_profile']}
        """
    )

    return {"research_findings": [{"agent": "operations", "findings": result.model_dump()}]}
