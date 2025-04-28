import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionDto } from '@/data/ImageDescriptionDto';
import axios, { AxiosResponse } from 'axios';

export async function processPhotos(taskId: number, prompt: string[], criteria: string[], images: any[]) {
    const processUrl = `${backendUrl}/processtask`;
    const payload = {
        taskId: taskId,
        taskPrompt: prompt.join('\n'),
        criteria: criteria,
        images: images
    };
    const response = await axios.post(processUrl, payload);
    return response.data;
}

export async function updateImageDescription(imgDescDto: ImageDescriptionDto): Promise<AxiosResponse> {
    return axios.put(`${backendUrl}/update-image-description`, { description: imgDescDto }, {
        headers: { "Content-Type": "application/json" }
    });
}