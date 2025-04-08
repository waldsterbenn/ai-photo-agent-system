
export class ImageDetectedObject {
    name: string
    confidence: number;
    attributes: string;
}
    
export class ImageDescription {
    filename: string;
    summary: string;
    scene: string;
    setting: string;
    text_content: string;
    objects: ImageDetectedObject[];
    delete: boolean;
    delete_reason: string;
    image_rank: number;
}