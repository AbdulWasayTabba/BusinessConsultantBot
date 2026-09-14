from graph.state import BizGPTState
from langchain_ollama import ChatOllama
from pydantic import BaseModel

class MarketingOutput(BaseModel):
    seo_landscape: str
    social_media: str
    advertising_strategy: str
    customer_acquisition: str

llm = ChatOllama(model="phi3:mini")
struct_llm = llm.with_structured_output(MarketingOutput)

with open("prompts/marketing_agent.txt", "r") as f:
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
    
    return {
        "research_findings": [{
            "agent": "marketing",
            "findings": result.model_dump()
        }]
    }