from pydantic import BaseModel


class AgentInstruction(BaseModel):
    name: str
    filename: str
    prompt: str
    criteria: str
