from pydantic import BaseModel

from config import get_llm, get_settings
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class ConsultantAgentOutput(BaseModel):
    analyze_SI: str
    solves_core_problem: str
    generate_recommendation: str
    strategic_direction: str


llm = get_llm(get_settings().consultant_model, streaming=True)
llm_struct = llm.with_structured_output(ConsultantAgentOutput)

# Note: Fixed the spelling to "consultant_agent.txt"
with open("prompts/consultant_agent.txt") as f:
    prompt = f.read()


def consultant_agent(state: BizGPTState):
    logger.info("node_enter", extra={"node": "consultant_agent"})
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
            result.strategic_direction,
        ]
    }
