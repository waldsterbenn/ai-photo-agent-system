from pydantic import BaseModel


class ImageDetectedObject(BaseModel):
    name: str
    confidence: float
    attributes: str
