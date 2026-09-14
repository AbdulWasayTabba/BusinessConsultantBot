from graph.state import BizGPTState
from langchain_ollama import ChatOllama
from pydantic import BaseModel

class CustomerOutput(BaseModel):
    customer_reviews: str
    pain_points: list[str]
    satisfaction: str
    retention: str

llm = ChatOllama(model="phi3:mini")
struct_llm = llm.with_structured_output(CustomerOutput)

with open("prompts/customer_agent.txt", "r") as f:
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
    
    return {
        "research_findings": [{
            "agent": "customer",
            "findings": result.model_dump()
        }]
    }