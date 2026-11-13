from graph.state import BizGPTState
from pydantic import BaseModel
from config import get_llm

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

with open("prompts/business_profiler.txt","r") as f:
    prompt = f.read()

def business_profiler(state:BizGPTState):
    print("entering business profiler")
    result = llm_struct.invoke(f"{prompt} \n user input : {state['user_input']}")

    return {"business_profile": result.model_dump()
    }

