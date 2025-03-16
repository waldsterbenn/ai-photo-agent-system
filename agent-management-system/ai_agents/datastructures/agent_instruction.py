from pydantic import BaseModel


class AgentInstruction(BaseModel):
    name: str
    prompt: str
    filename: str
