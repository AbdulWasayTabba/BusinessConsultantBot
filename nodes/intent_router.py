from graph.state import BizGPTState
from typing import Literal
from pydantic import BaseModel
from langchain_ollama import ChatOllama


class IntentRouterOutput(BaseModel):
    route_type: Literal["greeting" , "business_qa", "report_revision","follow_up_q"
                        , "business_analysis", "invalid"]

llm = ChatOllama(model="phi3:mini")
structured_llm = llm.with_structured_output(IntentRouterOutput)

with open("prompts/intent_router.txt",'r') as f:
    prompt = f.read()


def intent_router(state: BizGPTState):
    print("entering intent router")
    result  = structured_llm.invoke(
    f"{prompt}\n\nUser Input:\n{state.get('user_input', '')}"
)
    return {"route_type":result.route_type}

    