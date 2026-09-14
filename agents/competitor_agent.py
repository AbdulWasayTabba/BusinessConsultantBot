from graph.state import BizGPTState
from langchain_ollama import ChatOllama
from pydantic import BaseModel

class CompetitorOutput(BaseModel):
    competitor_landscape: str
    pricing_analysis: str
    positioning: str
    strengths_and_weaknesses: list[str]

llm = ChatOllama(model="phi3:mini")
struct_llm = llm.with_structured_output(CompetitorOutput)

with open("prompts/competitor_agent.txt", "r") as f:
    prompt = f.read()

def competitor_agent(state: BizGPTState):
    # Actually invoke the LLM with the prompt and state variables
    result = struct_llm.invoke(
        f"""
        {prompt} 
        
        Research Plan:
        {state['research_plan']}
        
        Business Profile:
        {state['business_profile']}
        """
    )
    
    # Return a dict targeting the state key, wrapping the output in a list
    return {
        "research_findings": [{
            "agent": "competitor",
            "findings": result.model_dump()
        }]
    }