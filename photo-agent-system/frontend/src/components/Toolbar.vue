<template>
    <div class="toolbar d-flex p-2 bg-secondary-subtle sticky-top hstack gap-3">
        <!-- Hidden File Input -->
        <input type="file" accept="image/*" multiple ref="imageInput" style="display:none"
            @change="handleImageUpload" />

        <!-- Gear icon button to open analysis modal -->
        <button @click="toolbarStore.openAnalysisModal" class="btn btn-secondary-subtle p-2" title="Analysis Settings">
            <i class="bi bi-gear"></i>
        </button>

        <!-- Button to trigger image picker -->
        <button @click="toolbarStore.triggerImagePicker(imageInput)" class="btn btn-secondary p-2 ms-auto"
            :disabled="!appStateStore.allSystemsNominal" title="Upload a photo">
            <i class="bi bi-image"></i> Select Photos
        </button>

        <input type="checkbox" class="btn-check" id="btn-check-duplicates" autocomplete="off"
            :disabled="disableDuplicateBtn || !appStateStore.allSystemsNominal"
            v-model="toolbarStore.searchForDuplicates" @click="toolbarStore.findDuplicates()" />
        <label class="btn btn-secondary p-2" for="btn-check-duplicates">
            Duplicates <i class="bi bi-copy"></i>
        </label>

        <button @click="onDeleteSelected" class="btn btn-secondary p-2" title="Delete selected photos"
            :disabled="disableDeleteBtn || !appStateStore.allSystemsNominal">
            <i class="bi bi-trash"></i>
        </button>

        <button @click="analyzePhotos" class="btn btn-primary p-2"
            :disabled="disableAnalyzeBtn || !appStateStore.allSystemsNominal"
            :title="disableAnalyzeBtn ? 'Working' : 'Nothing to analyse'">
            <span v-if="appLoading" class="spinner-border spinner-border-sm me-2" title="Working" role="status"
                aria-hidden="true"></span>
            <span>Analyze</span>
        </button>
    </div>
</template>

<script setup lang="ts">
import { processPhotos, updateImageDescription } from '@/api/analyzePhotosApi';
import { uploadImage } from '@/api/imageUploadApi';
import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionDto } from '@/data/ImageDescriptionDto';
import type { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { useAppStateStore } from '@/stores/appStateStore';
import { useImageDescriptionsStore } from '@/stores/imageDescriptionsStore';
import { useToolbarStore } from '@/stores/toolbarStore';
import { ImageTools } from '@/tools/ImageTools';
import { computed, ref } from 'vue';

const toolbarStore = useToolbarStore();
const imageDescriptionsStore = useImageDescriptionsStore();
const appStateStore = useAppStateStore();

const appLoading = computed(() => appStateStore.loading);

const imageInput = ref<HTMLInputElement | null>(null);

const maxFileSizeBytes = 2 * 1024 * 1024;
const compressImgUrl = `${backendUrl}/compress-image`;

const disableDeleteBtn = computed(() => !imageDescriptionsStore.imageDescriptions.some((x: ImageDescriptionViewModel) => x.delete));
const disableAnalyzeBtn = computed(() => !imageDescriptionsStore.imageDescriptions.some((imgDesc: ImageDescriptionViewModel) => !imgDesc.summary));
const disableDuplicateBtn = computed(() => imageDescriptionsStore.imageDescriptions.some((imgDesc: ImageDescriptionViewModel) => imgDesc.loading));

function setDescriptionsLoadingState(loadingState: boolean, selectedImages: ImageDescriptionViewModel[]) {
    selectedImages.forEach((image: ImageDescriptionViewModel) => {
        const index = imageDescriptionsStore.imageDescriptions.findIndex(
            (imgDesc: ImageDescriptionViewModel) => imgDesc.filename === image.filename
        );
        if (index !== -1) {
            imageDescriptionsStore.imageDescriptions[index].loading = loadingState;
        }
    });
}

async function onDeleteSelected() {
    const selectedImages = imageDescriptionsStore.imageDescriptions.filter((img: ImageDescriptionViewModel) => img.delete);
    if (selectedImages.length === 0) return;

    appStateStore.error = undefined;

    setDescriptionsLoadingState(true, selectedImages);

    try {
        await toolbarStore.deleteSelected(selectedImages);
    } catch (error: any) {
        console.error("Error deleting images:", error);
        appStateStore.error = error.message || JSON.stringify(error);
    } finally {
        appStateStore.loading = false;
    }
}

async function handleImageUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    if (!target.files || target.files.length === 0) return;

    appStateStore.error = undefined;

    // Add dummy cards immediately
    for (const file of Array.from(target.files)) {
        const dummyCard = {
            filename: file.name,
            dummy: true,
            loading: true,
        } as ImageDescriptionViewModel;
        imageDescriptionsStore.addImageDescription(dummyCard);
    }

    for (const file of Array.from(target.files)) {
        if (imageDescriptionsStore.imageDescriptions.some((imgDesc: ImageDescriptionViewModel) => !imgDesc.dummy && imgDesc.filename === file.name)) {
            appStateStore.error = `File ${file.name} already exists.`;
            imageDescriptionsStore.removeImageDescription(file.name);
            continue;
        }
        try {
            const tool = new ImageTools(compressImgUrl);
            const compressionResult = await tool.compressImage(file, maxFileSizeBytes);
            if (compressionResult.compressedSize > maxFileSizeBytes) {
                throw new Error("Image compression failed, its too big to analyse.");
            }

            const descriptionPayload = new ImageDescriptionDto();
            descriptionPayload.filename = file.name;
            descriptionPayload.thumbnail_base64 = compressionResult.compressImageBase64;
            descriptionPayload.metadata = compressionResult.metadata;

            const data = await uploadImage(file, descriptionPayload);
            imageDescriptionsStore.updateImageDescription({
                ...data,
                filename: file.name,
                dummy: false,
                loading: false,
                size_compressed_mb: compressionResult.compressedSize,
                size_uncompressed_mb: compressionResult.originalSize
            } as ImageDescriptionViewModel);
        } catch (err) {
            console.error("Image upload error:", err);
            appStateStore.error = (err as Error).message || JSON.stringify(err);
        }
    }

    target.value = "";
    appStateStore.loading = false;
}

async function analyzePhotos() {
    appStateStore.loading = true;
    appStateStore.error = undefined;
    const taskId = Date.now();

    // Get images that haven't been processed
    const filteredImages = imageDescriptionsStore.imageDescriptions
        .map((imgDesc: ImageDescriptionViewModel) => ({ ...imgDesc }))
        .filter((imgDesc: ImageDescriptionViewModel) => !imgDesc.summary);

    if (filteredImages.length === 0) {
        appStateStore.loading = false;
        return;
    }
    setDescriptionsLoadingState(true, filteredImages);
    try {
        const data = await processPhotos(taskId, appStateStore.getPrompt(), appStateStore.getSelectedCriteria(), filteredImages);
        if (data.status === "success" && taskId === data.taskId) {
            const returnData = JSON.parse(data.result);
            for (const newDesc of returnData) {
                const existingItem = imageDescriptionsStore.updateImageDescription(newDesc);
                if (!existingItem)
                    throw Error("ViewModel index not found.");
                const imgDescDto: ImageDescriptionDto = Object.assign(new ImageDescriptionDto(), existingItem);
                await updateImageDescription(imgDescDto);
            }
        } else {
            appStateStore.error = data.error;
        }
    } catch (err) {
        appStateStore.error = (err as Error).message || JSON.stringify(err);
    } finally {
        appStateStore.loading = false;
    }
}
</script>

<style scoped></style>