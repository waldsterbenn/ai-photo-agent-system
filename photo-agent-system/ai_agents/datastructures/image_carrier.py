from pydantic import BaseModel


class ImageCarrier(BaseModel):
    filename: str
    thumbnail_base64: str
    metadata: dict = None
