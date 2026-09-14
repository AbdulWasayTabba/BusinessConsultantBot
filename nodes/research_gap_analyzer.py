from pydantic import BaseModel
from langchain_ollama import ChatOllama
from graph.state import BizGPTState


class ResearchGapAnalyzerOutput(BaseModel):
    whats_missing: list[str]
    weak_evidence: list[str]
    prioritized_gaps: list[str]


llm = ChatOllama(model="llama3.2:3b")

llm_struct = llm.with_structured_output(
    ResearchGapAnalyzerOutput
)


with open("prompts/research_gap_analyzer.txt", "r") as f:
    prompt = f.read()


def research_gap_analyzer(state: BizGPTState):
    print("entering research gap analyzer")

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