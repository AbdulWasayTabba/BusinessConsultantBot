from pydantic import BaseModel
class WorkflowEvent(BaseModel):
    node: str
    status: str
    timestamp: str
    details: str