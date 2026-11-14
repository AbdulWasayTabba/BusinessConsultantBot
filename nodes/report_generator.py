from logging_setup import get_logger
from pydantic import BaseModel
from config import get_llm, get_settings
from graph.state import BizGPTState


logger = get_logger(__name__)

class ReportGeneratorOutput(BaseModel):
    executive_summary: str
    key_findings: list[str]
    recommendations: list[str]
    implementation_plan: str
    risks: list[str]
    expected_outcomes: list[str]


llm = get_llm(get_settings().consultant_model, streaming=True)

llm_struct = llm.with_structured_output(
    ReportGeneratorOutput
)


with open("prompts/report_generator.txt", "r") as f:
    prompt = f.read()


def report_generator(state: BizGPTState):
    logger.info("node_enter", extra={"node": "report_generator"})
    result = llm_struct.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Diagnosis:
        {state['diagnosis']}

        Research Findings:
        {state['research_findings']}

        Synthesized Insights:
        {state['synthesized_insights']}

        Recommendations:
        {state['recommendations']}

        Prioritized Actions:
        {state['prioritized_actions']}

        Implementation Plan:
        {state['implementation_plan']}

        Risk Review:
        {state['risk_review']}
        """
    )

    return {
        "final_report": result.model_dump()
    }