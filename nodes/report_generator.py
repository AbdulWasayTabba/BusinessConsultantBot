from pydantic import BaseModel
from langchain_ollama import ChatOllama
from graph.state import BizGPTState


class ReportGeneratorOutput(BaseModel):
    executive_summary: str
    key_findings: list[str]
    recommendations: list[str]
    implementation_plan: str
    risks: list[str]
    expected_outcomes: list[str]


llm = ChatOllama(model="qwen3:8b", streaming=True)

llm_struct = llm.with_structured_output(
    ReportGeneratorOutput
)


with open("prompts/report_generator.txt", "r") as f:
    prompt = f.read()


def report_generator(state: BizGPTState):
    print("entering report generator")
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