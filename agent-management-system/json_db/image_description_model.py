from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional


class ImageDescriptionModel(BaseModel):
    # id field auto-assigned; not required in POST
    id: Optional[int] = None
    filename: str
    summary: str
    scene: str
    setting: str
    text_content: str
    objects:  List[Dict[str, Any]]
    delete: bool
    delete_reason: str
    image_rank: int
    image_uri: str
