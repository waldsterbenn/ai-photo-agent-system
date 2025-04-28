import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionDto } from '@/data/ImageDescriptionDto';
import axios from 'axios';

export async function uploadImage(file: File, descriptionPayload: ImageDescriptionDto): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', JSON.stringify(descriptionPayload));

    const response = await axios.post(
        `${backendUrl}/create-image-description`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
    );
    return response.data;
}