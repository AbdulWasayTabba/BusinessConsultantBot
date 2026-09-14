from pydantic import BaseModel
from langchain_ollama import ChatOllama
from graph.state import BizGPTState

class ConsultantAgentOutput(BaseModel):
    analyze_SI: str
    solves_core_problem: str
    generate_recommendation: str
    strategic_direction: str

llm = ChatOllama(model="qwen3:8b",streaming=True)
llm_struct = llm.with_structured_output(ConsultantAgentOutput)

# Note: Fixed the spelling to "consultant_agent.txt"
with open("prompts/consultant_agent.txt", "r") as f:
    prompt = f.read()

def consultant_agent(state: BizGPTState):
    print("entering consulatant agent")
    result = llm_struct.invoke(f"""
        {prompt} 
        
        Business Profile:
        {state.get('business_profile', {})}
        
        Diagnosis:
        {state.get('diagnosis', {})}
        
        Synthesized Insights: 
        {state.get('synthesized_insights', [])}
        
        Research Gaps: 
        {state.get('research_gaps', [])}
    """)
    
    # Pack the Pydantic fields into a list of strings to match state.py
    return {
        "recommendations": [
            result.analyze_SI,
            result.solves_core_problem,
            result.generate_recommendation,
            result.strategic_direction
        ]
    }