from pydantic import BaseModel


class ImageCarrier(BaseModel):
    filename: str
    base64: str
    metadata: dict = None
