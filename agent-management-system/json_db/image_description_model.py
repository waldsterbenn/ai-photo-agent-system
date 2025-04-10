from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional


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
    quality_criteria: Optional[QualityCriteria]
