from logging_setup import get_logger
from pydantic import BaseModel
from config import get_llm, get_settings
from graph.state import BizGPTState


logger = get_logger(__name__)

class ResearchGapAnalyzerOutput(BaseModel):
    whats_missing: list[str]
    weak_evidence: list[str]
    prioritized_gaps: list[str]


llm = get_llm(get_settings().judge_model)

llm_struct = llm.with_structured_output(
    ResearchGapAnalyzerOutput
)


with open("prompts/research_gap_analyzer.txt", "r") as f:
    prompt = f.read()


def research_gap_analyzer(state: BizGPTState):
    logger.info("node_enter", extra={"node": "research_gap_analyzer"})

    result = llm_struct.invoke(
        f"""
        {prompt}

        Judge Feedback:
        {state['judge_feedback']}

        Recommendations:
        {state['recommendations']}

        Synthesized Insights:
        {state['synthesized_insights']}

        Diagnosis:
        {state['diagnosis']}
        """
    )

    return {
        "research_gaps": result.model_dump()
    }