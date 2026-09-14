from graph.state import BizGPTState
from typing import Literal
from pydantic import BaseModel
from langchain_ollama import ChatOllama

class ProblemClassifierOutput(BaseModel):
    problem_categories: list[
        Literal[
            "sales",
            "marketing",
            "operations",
            "finance",
            "pricing",
            "growth",
            "customer",
            "strategy",
            "technology",
            "other"
        ]
    ]

llm = ChatOllama(model="phi3:mini")
struct_llm = llm.with_structured_output(ProblemClassifierOutput)

with open("prompts/problem_classifier.txt","r") as f:
    prompt = f.read()

def problem_classifier(state: BizGPTState):

    print("entering problem classifier")

    result = struct_llm.invoke(
        f"""
        {prompt}

        Business Profile:
        {state['business_profile']}

        Diagnosis:
        {state['diagnosis']}

        User Input:
        {state['user_input']}
        """
    )

    return {
        "problem_categories": result.problem_categories
    }