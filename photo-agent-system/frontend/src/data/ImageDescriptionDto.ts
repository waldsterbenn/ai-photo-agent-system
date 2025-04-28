
export class ImageDetectedObjectDto {
    name: string
    confidence: number;
    attributes: string;
}
    
export class ImageDescriptionDto {
    filename: string;
    thumbnail_base64: string;
    summary: string;
    scene: string;
    setting: string;
    text_content: string;
    objects: ImageDetectedObjectDto[];
    delete: boolean;
    delete_reason: string;
    image_rank: number;
    keep_reason: string;
    forencic_analysis: string;
    quality_criteria: QualityCriteriaDto;
    metadata: any;
    
}

export class QualityCriteriaDto {
    low_quality: boolean;
    obscured_or_blurred: boolean;
    poor_lighting: boolean;
    poor_composition_or_framing: boolean;
    uninsterresting: boolean;
    poor_focus: boolean;
    poor_color_or_saturation: boolean;
    poor_contrast: boolean;
    noise_or_atifacts: boolean;
    closed_eyes: boolean;
    unflattering: boolean;
    poor_expression: boolean;
    finger_in_frame: boolean;
    bad_angle: boolean;
}