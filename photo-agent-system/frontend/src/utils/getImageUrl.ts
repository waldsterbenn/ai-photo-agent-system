export function getImageUrl(image: string): string {
    return image.startsWith('data:') ? image : `data:image/png;base64,${image}`;
}