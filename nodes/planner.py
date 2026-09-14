from graph.state import BizGPTState

from pydantic import BaseModel
from langchain_ollama import ChatOllama

class PlannerOutput(BaseModel):
    research_tasks: list[str]


llm = ChatOllama(model= "qwen3:8b",streaming=True)
struct_llm = llm.with_structured_output(PlannerOutput)


with open("prompts/planner.txt","r") as f:
    prompt = f.read()

def planner(state: BizGPTState):
    print("entering planner.py")

    result = struct_llm.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Diagnosis:
        {state['diagnosis']}

        Problem Categories:
        {state['problem_categories']}

        User Input:
        {state['user_input']}
        """
    )

    return {
        "research_plan": result.research_tasks
    }
