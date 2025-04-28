import { deleteSelectedImages } from '@/api/deleteSelectedImagesApi';
import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { defineStore } from 'pinia';
import { useImageDescriptionsStore } from './imageDescriptionsStore';

export const useToolbarStore = defineStore('toolbar', {
    state: () => ({
        searchForDuplicates: false,
        
    }),
    actions: {
        triggerImagePicker(imageInputEl: HTMLInputElement | null) {
            imageInputEl?.click();
        },
        handleImageUpload(event: Event) {
            console.log('Image upload event from store:', event);
        },
        openAnalysisModal() {
            const modalEl = document.getElementById('analysisModal');
            if (modalEl) {
                // eslint-disable-next-line no-undef
                new Modal(modalEl).show();
            }
        },
        findDuplicates() {
            this.searchForDuplicates = !this.searchForDuplicates;
        },
        async deleteSelected(
            imageDescriptions: ImageDescriptionViewModel[]            
        ) {            
            await deleteSelectedImages(imageDescriptions);            
            const imageDescriptionsStore = useImageDescriptionsStore();
            imageDescriptionsStore.setImageDescriptions(imageDescriptionsStore.imageDescriptions.filter(
                (imgDesc: ImageDescriptionViewModel) => !imgDesc.delete
            ));
        },
        analyzePhotos() {
            console.log('analyzePhotos from store');
        }
    }
});