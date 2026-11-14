from logging_setup import get_logger
from graph.state import BizGPTState
from pydantic import BaseModel
from config import get_llm



logger = get_logger(__name__)

class DiagnosisOutput(BaseModel):
    probable_root_causes: list[str]
    reasoning: str
    confidence_level: str

with open("prompts/diagnosis_agent.txt","r") as f:
    prompt = f.read()

llm = get_llm()

structured_llm = llm.with_structured_output(DiagnosisOutput)

def diagnosis_agent(state:BizGPTState):
    logger.info("node_enter", extra={"node": "diagnosis_agent"})
    result = structured_llm.invoke(f"{prompt}\n business profile {state['business_profile']} \n user input : {state['user_input']}")
    return {"diagnosis": result.model_dump()}

