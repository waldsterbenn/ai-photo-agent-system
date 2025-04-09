from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from datastructures.image_detected_object import ImageDetectedObject


class ImageDescription(BaseModel):
    filename: str
    summary: str
    scene: str
    setting: str
    forencic_analysis: str
    text_content: str
    objects: list[ImageDetectedObject]
    image_rank: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    delete: bool
    delete_reason: str
    keep_reason: str
