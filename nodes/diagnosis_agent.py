from graph.state import BizGPTState
from pydantic import BaseModel
from langchain_ollama import ChatOllama



class DiagnosisOutput(BaseModel):
    probable_root_causes: list[str]
    reasoning: str
    confidence_level: str

with open("prompts/diagnosis_agent.txt","r") as f:
    prompt = f.read()

llm = ChatOllama(model = "phi3:mini")

structured_llm = llm.with_structured_output(DiagnosisOutput)

def diagnosis_agent(state:BizGPTState):
    print("entering diagnosis agent")
    result = structured_llm.invoke(f"{prompt}\n business profile {state['business_profile']} \n user input : {state['user_input']}")
    return {"diagnosis": result.model_dump()}

