from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from datastructures.image_detected_object import ImageDetectedObject


class QualityCriteria(BaseModel):
    low_quality: bool
    obscured_or_blurred: bool
    poor_lighting: bool
    poor_composition_or_framing: bool
    uninsterresting: bool
    poor_focus: bool
    poor_color_or_saturation: bool
    poor_contrast: bool
    noise_or_atifacts: bool
    closed_eyes: bool
    unflattering: bool
    poor_expression: bool
    finger_in_frame: bool
    bad_angle: bool


class ImageDescription(BaseModel):
    filename: str
    summary: str
    scene: str
    setting: str
    forencic_analysis: str
    text_content: str
    objects: list[ImageDetectedObject]
    image_rank: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    quality_criteria: QualityCriteria
    delete: bool
    delete_reason: str
    keep_reason: str
