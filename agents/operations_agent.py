from graph.state import BizGPTState
from langchain_ollama import ChatOllama
from pydantic import BaseModel

class OperationsOutput(BaseModel):
    processes: str
    staffing: str
    inventory: str
    efficiency: str

llm = ChatOllama(model="phi3:mini")
struct_llm = llm.with_structured_output(OperationsOutput)

with open("prompts/operations_agent.txt", "r") as f:
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
    
    return {
        "research_findings": [{
            "agent": "operations",
            "findings": result.model_dump()
        }]
    }