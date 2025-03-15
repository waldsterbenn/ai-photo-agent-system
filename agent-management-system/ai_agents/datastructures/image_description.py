from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from datastructures.image_detected_object import ImageDetectedObject


class ImageDescription(BaseModel):
    summary: str
    scene: str
    # colors: list[str]
    setting: Literal['Indoor', 'Outdoor', 'Portrait', 'Landscape', 'Other']
    text_content: str
    objects: list[ImageDetectedObject]
    delete: bool
    delete_reason: str
    image_rank: Literal['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
