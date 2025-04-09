<template>
    <div class="container-fluid d-flex flex-column h-100">
        <!-- Toolbar -->
        <div class="toolbar d-flex p-2 bg-light sticky-top hstack gap-3">
            <!-- Hidden File Input -->
            <input type="file" accept="image/*" multiple ref="imageInput" style="display:none"
                @change="handleImageUpload" />

            <!-- Gear icon button to open analysis modal -->
            <button @click="openAnalysisModal" class="btn btn-secondary-subtle p-2" title="Analysis Settings">
                <i class="bi bi-gear"></i>
            </button>

            <!-- Button to trigger image picker -->
            <button @click="triggerImagePicker" class="btn btn-secondary p-2 ms-auto" title="Upload a photo">
                <i class="bi bi-image"></i> Select Photos
            </button>

            <div class="vr"></div>

            <!-- Button to delete photos -->
            <button @click="deleteSelected" class="btn btn-secondary p-2" title="Delete selected phots">
                <i class="bi bi-trash"></i>
            </button>

            <!-- Send Message Button -->
            <button @click="sendMessage" class="btn btn-primary p-2" :disabled="loading">Go</button>
        </div>

        <!-- Content area -->
        <div class="content flex-grow-1 p-2">
            <p v-if="loading">Working...</p>
            <p v-else-if="error">{{ error }}</p>

            <div v-if="imageDescriptions.length > 0" :class="`row row-cols-${columnsCount} g-3`">
                <div class="col" v-for="imgDesc in imageDescriptions" :key="imgDesc.filename">
                    <div class="card h-100 text-start">
                        <div class="position-relative">
                            <img :src="getImageURL(imgDesc.thumbnail_base64)" class="card-img-top img-thumbnail"
                                alt="Image">
                            <!-- Each image shows its own spinner if the system is loading -->
                            <div v-if="loading && !imgDesc.summary" class="spinner-overlay">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                        </div>
                        <div v-if="!!imgDesc.scene" class="card-body">
                            <div class="card-title d-flex justify-content-between align-items-center">
                                {{ imgDesc.filename }}
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" role="switch" value=""
                                        :id="`flexCheckDefault-${imgDesc.filename}`" v-model="imgDesc.delete">
                                    <label class="form-check-label" :for="`flexCheckDefault-${imgDesc.filename}`">
                                        <i class="bi bi-trash"></i>
                                    </label>
                                </div>
                            </div>
                            <div class="accordion mt-3" :id="`accordionDetails-${imgDesc.filename}`">
                                <div class="accordion-item">
                                    <h2 class="accordion-header" :id="`headingDetails-${imgDesc.filename}`">
                                        <button class="accordion-button collapsed" type="button"
                                            data-bs-toggle="collapse"
                                            :data-bs-target="`#collapseDetails-${imgDesc.filename}`"
                                            aria-expanded="false"
                                            :aria-controls="`collapseDetails-${imgDesc.filename}`">
                                            Quality {{ imgDesc.image_rank }}/10
                                        </button>
                                    </h2>
                                    <div :id="`collapseDetails-${imgDesc.filename}`" class="accordion-collapse collapse"
                                        :aria-labelledby="`headingDetails-${imgDesc.filename}`">
                                        <div class="accordion-body">

                                            <p class="card-text">
                                                <strong>The Photo:</strong>
                                                {{ imgDesc?.summary || '' }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Delete Reason:</strong> {{
                                                    imgDesc?.delete_reason || '' }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Scene:</strong> {{
                                                    imgDesc?.scene || ''
                                                }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Setting:</strong> {{
                                                    imgDesc?.setting || ''
                                                }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Text Content:</strong> {{
                                                    imgDesc?.text_content || ''
                                                }}
                                            </p>
                                            <div v-if="imgDesc?.objects?.length">
                                                <strong>Objects:</strong>
                                                <div>
                                                    <ul v-for="object in imgDesc.objects" :key="object.name"
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
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="card-body">
                            <div class="card-title d-flex justify-content-between align-items-center">
                                <div class="vstack">
                                    <div class="">{{ imgDesc.filename }}</div>
                                    <div class="hstack">
                                        <div class="p-2">
                                            <button @click="sendMessage" class="btn btn-outline-primary"
                                                :disabled="loading">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            Analyse
                                        </div>
                                        <div class="p-2  ms-auto">
                                            <div class="form-check form-switch">
                                                <input class="form-check-input" type="checkbox" role="switch" value=""
                                                    :id="`flexCheckDefault-${imgDesc.filename}`"
                                                    v-model="imgDesc.delete">
                                                <label class="form-check-label"
                                                    :for="`flexCheckDefault-${imgDesc.filename}`">
                                                    <i class="bi bi-trash"></i>
                                                </label>

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

<script setup lang="ts">
import axios from 'axios';
// Import Bootstrap Modal from bootstrap's JS distribution
import Modal from 'bootstrap/js/dist/modal';
import { computed, onMounted, ref, watch } from 'vue';
import { backendUrl } from '../config/backend_conf';
import criteriaData from '../config/criteria.json';
import promptsData from '../config/prompts.json';
import { ImageDescription } from '../data/ImageDescription';

const statusUrl = computed(() => `${backendUrl}/status`);
const processUrl = computed(() => `${backendUrl}/processtask`);
const deleteUrl = computed(() => `${backendUrl}/delete-image-descriptions`);
const imageDescriptions = ref<ImageDescription[]>([]); // Ensure descriptions include a "filename" property if available.
const loading = ref(false);
const error = ref('');
const imageInput = ref<HTMLInputElement | null>(null);
const columnsCount = ref(3);

// Import prompt options and set the default prompt
const promptsOptions = ref(promptsData.prompts);
const selectedPromptId = ref(promptsOptions.value[0].id);
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
watch(selectedPromptId, (newVal) => {
    const selected = promptsOptions.value.find(p => p.id === newVal);
    if (selected) {
        prompt.value = selected.prompt;
    }
});

// Get existing ImageDescriptions from backend and set them to the imageDescriptions ref.
async function fetchImageDescriptions() {
    console.log("Fetching image descriptions...");
    try {
        const response = await axios.get(`${backendUrl}/image-descriptions`);
        if (response.data.length === 0) {
            return;
        }
        imageDescriptions.value = response.data.map((desc: any) => Object.assign(new ImageDescription(), desc));

    } catch (err) {
        console.error("Error fetching image descriptions:", err);
    }
}
// Fetch image descriptions on component mount
onMounted(() => fetchImageDescriptions());

function triggerImagePicker() {
    imageInput.value?.click();
}

function getImageURL(image: string): string {
    return image.startsWith('data:') ? image : `data:image/png;base64,${image}`;
}

async function scaleImageFile(file: File, scaleFactor: number = 1): Promise<string> {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
            const width = img.width * scaleFactor;
            const height = img.height * scaleFactor;

            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            if (!ctx) {
                return reject(new Error("Unable to get canvas context"));
            }
            ctx.drawImage(img, 0, 0, width, height);
            resolve(canvas.toDataURL("image/png"));
        };
        img.onerror = (err) => reject(err);

        const reader = new FileReader();
        reader.onload = () => {
            if (typeof reader.result === "string") {
                img.src = reader.result;
            } else {
                reject(new Error("Unexpected result type."));
            }
        };
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}

async function handleImageUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    if (!target.files || target.files.length === 0) return;
    for (const file of Array.from(target.files)) {
        try {

            // Scale image for local preview
            const dataUrl = await scaleImageFile(file, 0.5);
            const base64Data = dataUrl.split(',')[1]; // Remove base64 prefix

            // Prepare description data (here, only the filename is provided)
            const descriptionPayload = new ImageDescription();
            descriptionPayload.filename = file.name;
            descriptionPayload.thumbnail_base64 = base64Data;

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
            // Optionally update the imageDescriptions array with the response
            imageDescriptions.value.push(response.data);
        } catch (err) {
            console.error("Image upload error:", err);
            error.value = (err as Error);
        }
    }
    target.value = "";
}

const sendMessage = async (e: Event) => {
    loading.value = true;
    error.value = "";
    try {
        const taskId = Date.now();

        const filteredImages = imageDescriptions.value.filter(image => !image.summary)
            .map(x => ({ filename: x.filename, thumbnail_base64: x.thumbnail_base64, metadata: {} }));

        if (filteredImages.length === 0) {
            loading.value = false;
            return;
        }
        // Only include criteria that are selected
        const selectedCriteria = criteria.value.filter(c => c.selected).map(c => c.text);
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
                const existingIndex = imageDescriptions.value.findIndex((desc) => desc.filename === newDesc.filename);
                if (existingIndex !== -1) {
                    imageDescriptions.value[existingIndex] = { ...imageDescriptions.value[existingIndex], ...newDesc };
                } else {
                    throw Error("Image index not found. This shouldnt happen since images are always created before processing");
                }

                try {
                    const existing = imageDescriptions.value[existingIndex];
                    await axios.put(`${backendUrl}/update-image-description`, { description: existing }, {
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
};

async function deleteSelected(params: Event) {
    loading.value = true;
    error.value = "";
    try {
        const selectedImages = imageDescriptions.value.filter(imgDesc => imgDesc.delete);
        if (selectedImages.length === 0) return;

        const payload = {
            taskId: Date.now(),
            ids: selectedImages.map(x => ({ id: x.id }))
        };
        const response = await axios.delete(deleteUrl.value, { data: payload });
        if (response.status === 200) {
            imageDescriptions.value = imageDescriptions.value.filter(image => !image.delete);
        } else {
            error.value = data.error;
        }
    } catch (err) {
        error.value = (err as Error).stack ? (err as Error).message : JSON.stringify(err);
    } finally {
        loading.value = false;
    }
}

const fetchStatus = async () => {
    try {
        const response = await axios.get(statusUrl.value);
        imageDescriptions.value = JSON.stringify(response.data);
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};

function updateDeleteStatus(filename: string, value: boolean) {
    const description = getDescription(filename);
    if (description) {
        description.delete = value;
    }
}

function openAnalysisModal() {
    const modalEl = document.getElementById('analysisModal');
    if (modalEl) {
        const modal = new Modal(modalEl);
        modal.show();
    }
}

</script>

<style scoped>
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