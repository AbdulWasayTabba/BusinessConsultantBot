from pydantic import BaseModel
from graph.state import BizGPTState
from langchain_ollama import ChatOllama

class MissingInfo(BaseModel):
    info_required:list[str]
    question:str

llm = ChatOllama(model="phi3:mini")

llm_struct = llm.with_structured_output(MissingInfo)

with open("prompts/missing_info.txt","r") as f:
    prompt = f.read()

def missing_info(state:BizGPTState):
    result = llm_struct.invoke(f"""{prompt}
                    User Input: {state.get("user_input", "")}
                    Business Profile: {state.get("business_profile", {})}""")
    return {
        "missing_fields":result.info_required,
        "clarification_question": result.question
    }