import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import axios from 'axios';

export async function deleteSelectedImages(
    selectedImages: ImageDescriptionViewModel[]
): Promise<boolean> {
    const deleteUrl = `${backendUrl}/delete-image-descriptions`;
    
    const payload = {
        taskId: Date.now(),
        ids: selectedImages.map(img => ({ id: img.id }))
    };

    const response = await axios.delete(deleteUrl, { data: payload });
    if (response.status === 200) {
        return true;
    }
    throw new Error(response.data.error || 'Deletion failed');
}