from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState


class MissingInfo(BaseModel):
    info_required: list[str]
    question: str


llm = get_llm()

llm_struct = llm.with_structured_output(MissingInfo)

with open("prompts/missing_info.txt") as f:
    prompt = f.read()


def missing_info(state: BizGPTState) -> dict:
    result = llm_struct.invoke(f"""{prompt}
                    User Input: {state.get("user_input", "")}
                    Business Profile: {state.get("business_profile", {})}""")
    return {"missing_fields": result.info_required, "clarification_question": result.question}
