import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { useImageDescriptionsStore } from '@/stores/imageDescriptionsStore';
import axios from 'axios';

export async function fetchImageDescriptions(): Promise<void> {
    const imageDescriptionsStore = useImageDescriptionsStore();
    console.log("Fetching image descriptions...");
    try {
        const countResponse = await axios.get(`${backendUrl}/image-descriptions-count`);
        if (countResponse.data === 0) {
            return;
        }
        const range = Array.from({ length: countResponse.data }, (_, i) => i);
        const dummies = range.map((i) => ({
            id: i,
            dummy: true,
            loading: true,
        }));
        imageDescriptionsStore.setImageDescriptions(dummies);

        const response = await axios.get(`${backendUrl}/image-descriptions`);
        if (response.data.length === 0) {
            return;
        }
        imageDescriptionsStore.setImageDescriptions(
            response.data.map(
                (desc: any) => Object.assign(new ImageDescriptionViewModel(), desc)
            )
        );
    } catch (err) {
        console.error("Error fetching image descriptions:", err);
        throw err;
    }
}