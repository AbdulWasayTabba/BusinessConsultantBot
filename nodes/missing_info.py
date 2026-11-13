from pydantic import BaseModel
from graph.state import BizGPTState
from config import get_llm

class MissingInfo(BaseModel):
    info_required:list[str]
    question:str

llm = get_llm()

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