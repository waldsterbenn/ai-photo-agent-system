import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { defineStore } from 'pinia';

export const useImageDescriptionsStore = defineStore('imageDescriptions', {
    state: (): { imageDescriptions: ImageDescriptionViewModel[] } => ({
        imageDescriptions: [] as ImageDescriptionViewModel[],
    }),
    actions: {
        setImageDescriptions(newImages: ImageDescriptionViewModel[]) {
            this.imageDescriptions = newImages;
        },
        addImageDescription(imageDesc: ImageDescriptionViewModel) {
            this.imageDescriptions.push(imageDesc);
        },
        removeImageDescription(filename: string) {
            const index = this.imageDescriptions.findIndex((desc) => desc.filename === filename && desc.dummy);
            this.imageDescriptions.splice(index, 1);
        },
        updateImageDescription(updatedData: Partial<ImageDescriptionViewModel>):ImageDescriptionViewModel|undefined {
            const index = this.imageDescriptions.findIndex((desc) => desc.filename === updatedData.filename);
            if (index !== -1) {
                const newLocal = {
                    ...this.imageDescriptions[index],
                    ...updatedData,
                    dummy: false,
                    loading: false,
                } as ImageDescriptionViewModel;
                this.imageDescriptions[index] = newLocal;
                return this.imageDescriptions[index];
            }
            return undefined;
        },
    },
});