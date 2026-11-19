from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class TargetedResearchOutput(BaseModel):
    new_findings: list[str]
    evidence_added: list[str]


llm = get_llm(temperature=0)

llm_struct = llm.with_structured_output(TargetedResearchOutput)


with open("prompts/targeted_research.txt") as f:
    prompt = f.read()


def targeted_research(state: BizGPTState):
    logger.info("node_enter", extra={"node": "targeted_research"})

    result = llm_struct.invoke(
        f"""
        {prompt}

        Business Profile:
        {state.get("business_profile", {})}

        Diagnosis:
        {state.get("diagnosis", {})}

        Existing Research Findings:
        {state.get("research_findings", [])}

        Research Gaps:
        {state.get("research_gaps", {})}
        """
    )

    return {
        "research_findings": [
            {
                "agent": "targeted_research",
                "findings": result.new_findings,
                "evidence_added": result.evidence_added,
            }
        ]
    }
