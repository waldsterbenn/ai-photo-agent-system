<script setup lang="ts">
import axios from 'axios';
import { defineAsyncComponent } from 'vue';
// Import Bootstrap Modal from bootstrap's JS distribution
import { backendUrl } from '@/config/backend_conf';
import * as criteriaData from '@/config/criteria.json';
import * as promptsData from '@/config/prompts.json';
import { ImageDescriptionDto } from '@/data/ImageDescriptionDto';
import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { ImageTools } from '@/tools/ImageTools';
import Modal from 'bootstrap/js/dist/modal';
import { computed, onMounted, ref, toRaw, watch } from 'vue';
import Toolbar from './Toolbar.vue';


// Import DuplicateImages component asynchronously
const DuplicateImages = defineAsyncComponent(() => import('./DuplicateImages.vue'));
const searchForDuplicates = ref<boolean>(false);

const processUrl = computed(() => `${backendUrl}/processtask`);
const deleteUrl = computed(() => `${backendUrl}/delete-image-descriptions`);
const compressImgUrl = computed(() => `${backendUrl}/compress-image`);
const imageDescriptions = ref<ImageDescriptionViewModel[]>([]); // Ensure descriptions include a "filename" property if available.
const loading = ref(false);
const error = ref('');
const imageInput = ref<HTMLInputElement | null>(null);
const columnsCount = ref(3);

const maxFileSizeBytes = 2 * 1024 * 1024; // MB
const duplicateTimeThresholdMs = 10 * 1000; // milliseconds

// Import prompt options and set the default prompt
const promptsOptions = ref(promptsData.prompts);
const selectedPromptId = ref<number>(promptsOptions.value[0].id);
const taskPrompt = promptsOptions.value[0].prompt;
const prompt = ref(taskPrompt);

// Update criteria: convert array of strings to objects with selected=true
const criteriaSingleImagePrompt = criteriaData.criteria;
const criteria = ref(
    criteriaSingleImagePrompt.map((crit: string) => ({
        text: crit,
        selected: true
    }))
);

// Update the main prompt when a new prompt is selected.
watch(selectedPromptId, (selectedId: number) => {
    const selected = promptsOptions.value.find((p: { id: number; }) => p.id === selectedId);
    if (selected) {
        prompt.value = selected.prompt;
    }
});

// Get existing ImageDescriptions from backend and set them to the imageDescriptions ref.
async function fetchImageDescriptions() {
    console.log("Fetching image descriptions...");
    try {
        const count = await axios.get(`${backendUrl}/image-descriptions-count`);
        if (count.data === 0) {
            return;
        }

        // Create a dummy cards immediately
        const range = Array.from({ length: count.data }, (_, i) => i);
        const dummies = range.map((i) =>
        ({
            id: i,
            dummy: true,
            loading: true,
        }));
        imageDescriptions.value = dummies;

        const response = await axios.get(`${backendUrl}/image-descriptions`);
        if (response.data.length === 0) {
            return;
        }
        imageDescriptions.value = response.data.map((desc: any) => Object.assign(new ImageDescriptionViewModel(), desc));

    } catch (err) {
        console.error("Error fetching image descriptions:", err);
        error.value = (err as Error);
    }
}

async function makePlaceholderDescriptions() {
    console.log("Counting image descriptions...");
    try {
        const count = await axios.get(`${backendUrl}/image-descriptions-count`);
        if (count.data === 0) {
            return;
        }
        const range = Array.from({ length: count.data }, (_, i) => i);
        const dummies = range.map((i) =>
        ({
            id: i,
            dummy: true,
            loading: true,
        }));
        imageDescriptions.value = dummies;
    } catch (err) {
        console.error("Error counting image descriptions:", err);
        error.value = (err as Error);
    }
}

// Fetch image descriptions on component mount
onMounted(() => {
    makePlaceholderDescriptions(); //Quick
    fetchImageDescriptions() //Slow
});

function triggerImagePicker() {
    imageInput.value?.click();
}

function getImageURL(image: string): string {
    return image.startsWith('data:') ? image : `data:image/png;base64,${image}`;
}

async function handleImageUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    if (!target.files || target.files.length === 0) return;

    // Create a dummy cards immediately
    for (const file of Array.from(target.files)) {

        const dummyCard = {
            id: Date.now(),
            filename: file.name,
            dummy: true,
            loading: true,
        };
        imageDescriptions.value.push(dummyCard);
    }

    for (const file of Array.from(target.files)) {

        try {
            const tool = new ImageTools(compressImgUrl.value);
            const compressionResult = await tool.compressImage(file, maxFileSizeBytes);
            if (compressionResult.compressedSize > maxFileSizeBytes) {
                throw new Error("Image compression failed, its too big to analyse.");
            }

            const descriptionPayload = new ImageDescriptionDto();
            descriptionPayload.filename = file.name;
            descriptionPayload.thumbnail_base64 = compressionResult.compressImageBase64;
            descriptionPayload.metadata = compressionResult.metadata;

            // Prepare multipart/form-data
            const formData = new FormData();
            formData.append('file', file);
            formData.append('description', JSON.stringify(descriptionPayload));

            // Call create-image-description endpoint
            const response = await axios.post(
                `${backendUrl}/create-image-description`,
                formData,
                {
                    headers: { "Content-Type": "multipart/form-data" }
                }
            );
            // Update the dummy card with the server response data
            const index = imageDescriptions.value.findIndex(img =>
                img.filename === file.name && img.dummy === true
            );
            if (index !== -1) {
                imageDescriptions.value[index] = { ...response.data, dummy: false, loading: false };
            }
        } catch (err) {
            console.error("Image upload error:", err);
            error.value = (err as Error).message || JSON.stringify(err);
        }
    }
    target.value = "";
}

async function sendMessage(e: Event) {
    loading.value = true;
    error.value = "";
    try {
        const taskId = Date.now();

        // Crude way of checking if the image is being processed or not. TODO: Improve this.
        const filteredImages = imageDescriptions.value
            .map((imgDesc: ImageDescriptionViewModel) => toRaw(imgDesc))
            .filter((imgDesc: ImageDescriptionViewModel) => !imgDesc.summary);

        if (filteredImages.length === 0) {
            loading.value = false;
            return;
        }
        setLoadingState(true, filteredImages);

        // Only include criteria that are selected
        const selectedCriteria = criteria.value.filter((c: { selected: boolean; }) => c.selected).map((c: { text: string; }) => c.text);
        const payload = {
            taskId: taskId,
            taskPrompt: prompt.value.join('\n'),
            criteria: selectedCriteria,
            images: filteredImages
        };
        const response = await axios.post(processUrl.value, payload);
        const data = response.data;
        if (data.status === "success" && taskId === data.taskId) {
            const returnData = JSON.parse(data.result);
            for (const newDesc of returnData) {
                const existingIndex = imageDescriptions.value.findIndex((imgDesc: ImageDescriptionViewModel) => imgDesc.filename === newDesc.filename);
                if (existingIndex !== -1) {
                    imageDescriptions.value[existingIndex] = { ...imageDescriptions.value[existingIndex], ...newDesc, dummy: false, loading: false };
                } else {
                    throw Error("ViewModel index not found. This shouldnt happen since images are always created before processing");
                }

                try {
                    const imgDescDto = Object.assign(new ImageDescriptionDto(), imageDescriptions.value[existingIndex]);
                    await axios.put(`${backendUrl}/update-image-description`, { description: imgDescDto }, {
                        headers: { "Content-Type": "application/json" }
                    });
                } catch (err) {
                    error.value = (err as Error).stack ? (err as Error).message : JSON.stringify(err);
                    console.error("Error updating image description:", err);
                }
            }
        } else {
            error.value = data.error;
        }
    } catch (err) {
        error.value = (err as Error).stack ? (err as Error).message : JSON.stringify(err);
    } finally {
        loading.value = false;
    }
}

async function deleteSelected(params: Event) {
    loading.value = true;
    error.value = "";
    try {
        const selectedImages = imageDescriptions.value.filter((imgDesc: { delete: any; }) => imgDesc.delete);
        if (selectedImages.length === 0) return;
        setLoadingState(true, selectedImages);
        const payload = {
            taskId: Date.now(),
            ids: selectedImages.map((x: { id: any; }) => ({ id: x.id }))
        };
        const response = await axios.delete(deleteUrl.value, { data: payload });
        if (response.status === 200) {
            imageDescriptions.value = imageDescriptions.value.filter((image: { delete: any; }) => !image.delete);
        } else {
            error.value = data.error;
        }
    } catch (err) {
        error.value = (err as Error).stack ? (err as Error).message : JSON.stringify(err);
    } finally {
        loading.value = false;
    }
}

function openAnalysisModal() {
    const modalEl = document.getElementById('analysisModal');
    if (modalEl) {
        const modal = new Modal(modalEl);
        modal.show();
    }
}

function getBrowserLocale() {
    let lang;
    if (navigator.languages && navigator.languages.length) {
        lang = navigator.languages;
    }
    lang = navigator.language;
    return "da-DK"; //TODO make this selectable from browsers languages or custom list

}

function findDuplicates() {
    searchForDuplicates.value = !searchForDuplicates.value;
}

function setLoadingState(loading: boolean, selectedImages: ImageDescriptionViewModel[]) {
    selectedImages.forEach((image: ImageDescriptionViewModel) => {
        const index = imageDescriptions.value.findIndex((imgDesc: ImageDescriptionViewModel) => imgDesc.id === image.id);
        if (index !== -1) {
            imageDescriptions.value[index].loading = loading;
        }
    });
}

</script>

<template>
    <div class="container-fluid d-flex flex-column h-100 bg-secondary-subtle">
        <!-- Toolbar -->
        <Toolbar @handleImageUpload="handleImageUpload" @openAnalysisModal="openAnalysisModal"
            @triggerImagePicker="triggerImagePicker" @findDuplicates="findDuplicates" @deleteSelected="deleteSelected"
            @sendMessage="sendMessage" />

        <div>
            <Suspense v-if="searchForDuplicates">
                <div class="content flex-grow-1 p-2 bg-secondary">
                    <!-- Replace duplicate logic with the new async component -->
                    <DuplicateImages :imageDescriptions="imageDescriptions" :getImageURL="getImageURL"
                        :getBrowserLocale="getBrowserLocale" :duplicateTimeThresholdMs="duplicateTimeThresholdMs" />
                </div>
                <template #fallback>

                    <div class="text-center">
                        <div class="d-flex align-items-center">
                            <strong role="status">Searching for duplicates...</strong>
                            <div class="spinner-border ms-auto" aria-hidden="true"></div>
                        </div>
                    </div>
                </template>
            </Suspense>
        </div>
        <div class="hr"></div>
        <!-- Content area -->

        <div class="content flex-grow-1 p-2">
            <p v-if="loading">Working...</p>
            <p v-else-if="error">{{ error }}</p>

            <div v-if="imageDescriptions.length > 0" :class="`row row-cols-${columnsCount} g-3`">
                <div class="col" v-for="imgDescVm in imageDescriptions" :key="imgDescVm.filename">
                    <div
                        :class="`card h-100 text-center position-relative ${imgDescVm.delete ? 'border border-danger' : ''}`">

                        <div class="position-relative">
                            <img v-if="imgDescVm.dummy"
                                :src="'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjwvc3ZnPg=='"
                                class="card-img-top img-thumbnail" alt="Image">
                            <img v-else :src="getImageURL(imgDescVm.thumbnail_base64)"
                                class="card-img-top img-thumbnail" alt="Image">

                            <div v-if="imgDescVm.loading" class="spinner-overlay">
                                <div class="spinner-border" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>

                        </div>
                        <button v-if="!imgDescVm.dummy" @click.stop="imgDescVm.delete = !imgDescVm.delete"
                            class="btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2"
                            title="Toggle delete">
                            <i class="bi bi-x"></i>
                        </button>
                        <div v-if="!!imgDescVm.scene" class="card-body">
                            <div class="card-title d-flex justify-content-between align-items-center">
                                {{ imgDescVm.filename }}
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" role="switch" value=""
                                        :id="`flexCheckDefault-${imgDescVm.filename}`" v-model="imgDescVm.delete">
                                    <label class="form-check-label" :for="`flexCheckDefault-${imgDescVm.filename}`">
                                        <i class="bi bi-trash"></i>
                                    </label>
                                </div>
                            </div>
                            <div class="accordion mt-3" :id="`accordionDetails-${imgDescVm.filename}`">
                                <div class="accordion-item">
                                    <h2 class="accordion-header" :id="`headingDetails-${imgDescVm.filename}`">
                                        <button class="accordion-button collapsed" type="button"
                                            data-bs-toggle="collapse"
                                            :data-bs-target="`#collapseDetails-${imgDescVm.filename}`"
                                            aria-expanded="false"
                                            :aria-controls="`collapseDetails-${imgDescVm.filename}`">
                                            Quality {{ imgDescVm.image_rank }}/10
                                        </button>
                                    </h2>
                                    <div :id="`collapseDetails-${imgDescVm.filename}`"
                                        class="accordion-collapse collapse"
                                        :aria-labelledby="`headingDetails-${imgDescVm.filename}`">
                                        <div class="accordion-body">

                                            <div v-if="imgDescVm?.metadata && Object.keys(imgDescVm.metadata).length > 0"
                                                class="card-text">
                                                {{
                                                    imgDescVm?.metadata["exif"]["0th"]["Make"] || ''
                                                }}
                                                <div class="vr"></div>
                                                {{
                                                    new Date(imgDescVm?.metadata["exif"]["0th"]["DateTime"]
                                                        .replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
                                                        .replace(' ', 'T')).toLocaleString(getBrowserLocale()) || ''
                                                }}
                                                <!-- {{ imgDesc?.metadata }} -->
                                            </div>

                                            <p class="card-text">
                                                <strong>Photo:</strong>
                                                {{ imgDescVm?.summary || '' }}
                                            </p>

                                            <p v-if="imgDescVm?.delete_reason" class="card-text">
                                                <strong>Delete:</strong> {{
                                                    imgDescVm?.delete_reason || '' }}
                                            </p>

                                            <p v-if="imgDescVm?.keep_reason" class="card-text">
                                                <strong>Keep:</strong> {{
                                                    imgDescVm?.keep_reason || ''
                                                }}
                                            </p>
                                            <p v-if="imgDescVm?.scene" class="card-text">
                                                <strong>Scene:</strong> {{
                                                    imgDescVm?.scene || ''
                                                }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Setting:</strong> {{
                                                    imgDescVm?.setting || ''
                                                }}
                                            </p>
                                            <p v-if="imgDescVm?.text_content" class="card-text">
                                                <strong>Text Content:</strong> {{
                                                    imgDescVm?.text_content || ''
                                                }}
                                            </p>

                                            <p v-if="imgDescVm?.forencic_analysis" class="card-text">
                                                <strong>Analysis:</strong> {{
                                                    imgDescVm?.forencic_analysis || ''
                                                }}
                                            </p>

                                            <div v-if="imgDescVm?.objects?.length">
                                                <strong>Objects:</strong>
                                                <div>
                                                    <ul v-for="object in imgDescVm.objects" :key="object.name"
                                                        class="list-group">
                                                        <li class="list-group-item d-flex align-items-start">
                                                            <div class="ms-2 me-auto">
                                                                <div class="fw-italic">{{ object.name }}
                                                                </div>
                                                                {{ object.attributes }}
                                                            </div>
                                                        </li>
                                                    </ul>
                                                </div>
                                            </div>

                                            <p v-if="imgDescVm?.quality_criteria" class="card-text">
                                                <strong>Quality Checks:</strong> {{
                                                    imgDescVm?.quality_criteria || ''
                                                }}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="card-body">
                            <div class="card-title d-flex justify-content-between align-items-center">
                                <div class="vstack">
                                    <div class="hstack">
                                        <!-- <div class="p-2">
                                            <button @click="sendMessage" class="btn btn-outline-primary"
                                                :disabled="loading">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            Analyse
                                        </div> -->
                                        <div class="p-2  ms-auto">
                                            <div class="form-check form-switch">
                                                <input class="form-check-input" type="checkbox" role="switch" value=""
                                                    :id="`flexCheckDefault-${imgDescVm.filename}`"
                                                    v-model="imgDescVm.delete">
                                                <label class="form-check-label"
                                                    :for="`flexCheckDefault-${imgDescVm.filename}`">
                                                    <i class="bi bi-trash"></i>
                                                </label>

                                            </div>
                                        </div>
                                    </div>
                                    <div class="card-text">
                                        <div class="card-text text-secondary">{{ imgDescVm.filename }}</div>
                                        <div v-if="imgDescVm?.metadata && Object.keys(imgDescVm.metadata).length > 0"
                                            class="card-text text-secondary">
                                            {{
                                                new Date(imgDescVm?.metadata["exif"]["0th"]["DateTime"]
                                                    .replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
                                                    .replace(' ', 'T')).toLocaleString(getBrowserLocale()) || ''
                                            }}
                                            <div class="vr"></div>
                                            {{
                                                imgDescVm?.metadata["exif"]["0th"]["Make"] || ''
                                            }}

                                            <!-- {{ imgDesc?.metadata }} -->
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Analysis Modal -->
    <div class="modal fade" id="analysisModal" tabindex="-1" aria-labelledby="analysisModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="analysisModalLabel">Configuration</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <h4>Profile</h4>
                    <select class="form-select mb-3" v-model.number="selectedPromptId">
                        <option v-for="p in promptsOptions" :key="p.id" :value="p.id">
                            {{ p.name }}
                        </option>
                    </select>
                    <h4 class="mt-3">Card Columns</h4>
                    <select class="form-select mb-3" v-model.number="columnsCount">
                        <option v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{ n }}</option>
                    </select>

                    <h4>Prompt</h4>
                    <ul class="">
                        <li v-for="(pr, index) in prompt" :key="index">
                            <div class="">{{ pr }}</div>
                        </li>
                    </ul>

                    <h4>Deletion criteria</h4>
                    <ul class="list-group m-2">
                        <li v-for="(crit, index) in criteria" :key="index"
                            class="list-group-item d-flex align-items-center">
                            <input type="checkbox" v-model="crit.selected" class="form-check-input me-2"
                                :id="`criteria-${index}`" />
                            <label :for="`criteria-${index}`" class="mb-0">{{ crit.text }}</label>
                        </li>
                    </ul>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Ok</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="css">
.position-relative {
    position: relative;
}

.spinner-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}
</style>