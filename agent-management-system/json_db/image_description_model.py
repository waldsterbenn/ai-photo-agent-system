from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional


class ImageDescriptionModel(BaseModel):
    # id field auto-assigned; not required in POST
    id: Optional[int] = None
    filename: str
    image_uri: str
    thumbnail_base64: str
    summary: Optional[str]
    scene: Optional[str]
    setting: Optional[str]
    text_content: Optional[str]
    objects:  Optional[List[Dict[str, Any]]]
    delete: Optional[bool]
    delete_reason: Optional[str]
    image_rank: Optional[int]
    keep_reason: Optional[str]
    forencic_analysis: Optional[str]
