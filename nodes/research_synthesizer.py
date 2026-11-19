from pydantic import BaseModel

from config import get_llm, get_settings
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)

llm = get_llm(get_settings().consultant_model)


class ResearchSynthesizerOutput(BaseModel):
    all_outputs_combined: str
    key_insights: str
    patterns: str
    evident_gaps: str


llm_struct = llm.with_structured_output(ResearchSynthesizerOutput)

with open("prompts/research_synthesizer.txt") as f:
    prompt = f.read()


def research_synthesizer(state: BizGPTState):
    logger.info("node_enter", extra={"node": "research_synthesizer"})
    # Create a string to hold all the collected research
    combined_research = ""

    # Loop through the list of dictionaries directly
    for finding in state.get("research_findings", []):
        agent_name = finding.get("agent", "Unknown")
        agent_data = finding.get("findings", {})
        combined_research += f"\n--- {agent_name.upper()} AGENT FINDINGS ---\n{agent_data}\n"

    # Invoke your structured LLM with the prompt and the compiled data
    result = llm_struct.invoke(
        f"""
        {prompt}

        Here are the research findings from the parallel team:
        {combined_research}
        
        Business Profile:
        {state.get('business_profile', {})}
        
        Diagnosis:
        {state.get('diagnosis', {})}
        """
    )

    # Return the keys matching your ResearchSynthesizerOutput model
    return {
        "synthesized_insights": [
            result.key_insights,
            result.patterns,
        ],  # Adjust based on how you want to map it to state.py
        "research_gaps": [
            result.evident_gaps
        ],  # Note: check spelling of evidence_gaps in your Pydantic model!
    }
