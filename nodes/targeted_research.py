from langchain_ollama import ChatOllama
from pydantic import BaseModel

from graph.state import BizGPTState


class TargetedResearchOutput(BaseModel):
    new_findings: list[str]
    evidence_added: list[str]


llm = ChatOllama(
    model="phi3:mini",
    temperature=0
)

llm_struct = llm.with_structured_output(
    TargetedResearchOutput
)


with open("prompts/targeted_research.txt", "r") as f:
    prompt = f.read()


def targeted_research(state: BizGPTState):
    print("entering targeted research")

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
                "evidence_added": result.evidence_added
            }
        ]
    }