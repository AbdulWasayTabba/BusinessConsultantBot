from pydantic import BaseModel

from config import get_llm
from graph.state import BizGPTState
from logging_setup import get_logger

logger = get_logger(__name__)


class BusinessProfilerOutput(BaseModel):
    industry: str
    revenue: str
    employees: str
    location: str
    business_model: str
    target_customers: str
    pain_points: list[str]
    business_stage: str


llm = get_llm()

llm_struct = llm.with_structured_output(BusinessProfilerOutput)

with open("prompts/business_profiler.txt") as f:
    prompt = f.read()


def business_profiler(state: BizGPTState):
    logger.info("node_enter", extra={"node": "business_profiler"})
    result = llm_struct.invoke(f"{prompt} \n user input : {state['user_input']}")

    return {"business_profile": result.model_dump()}
