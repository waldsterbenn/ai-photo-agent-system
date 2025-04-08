<template>
    <div class="container-fluid d-flex flex-column h-100">
        <!-- Toolbar -->
        <div class="toolbar d-flex p-2 bg-light sticky-top hstack gap-3">
            <!-- Hidden File Input -->
            <input type="file" accept="image/*" multiple ref="imageInput" style="display:none"
                @change="handleImageUpload" />

            <!-- Gear icon button to open analysis modal -->
            <button @click="openAnalysisModal" class="btn btn-secondary p-2" title="Analysis Settings">
                <i class="bi bi-gear"></i>
            </button>

            <!-- Button to trigger image picker -->
            <button @click="triggerImagePicker" class="btn btn-secondary p-2 ms-auto" title="Upload an image">
                <i class="bi bi-image"></i> Select Photos
            </button>

            <div class="vr"></div>

            <!-- Send Message Button -->
            <button @click="sendMessage" class="btn btn-primary p-2">Go</button>
        </div>

        <!-- Content area -->
        <div class="content flex-grow-1 p-2">
            <p v-if="loading">Working...</p>
            <p v-else-if="error">{{ error }}</p>

            <div v-if="images.length > 0" class="row">
                <div class="col-md-4 mb-3" v-for="image in images" :key="image.filename">
                    <div class="card h-100 text-start">
                        {{ image.filename }}
                        <div class="position-relative">
                            <img :src="getImageURL(image.base64)" class="card-img-top img-thumbnail" alt="Image">
                            <!-- Each image shows its own spinner if the system is loading -->
                            <div v-if="loading" class="spinner-overlay">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                        </div>
                        <div v-if="getDescription(image.filename)" class="card-body">
                            <div class="form-check form-switch">

                                <input class="form-check-input" type="checkbox" role="switch" value=""
                                    :id="`flexCheckDefault-${image.filename}`"
                                    :checked="getDescription(image.filename)?.delete">
                                <label class="form-check-label" :for="`flexCheckDefault-${image.filename}`">
                                    Should be deleted
                                </label>
                            </div>
                            <div class="accordion mt-3" :id="`accordionDetails-${image.filename}`">
                                <div class="accordion-item">
                                    <h2 class="accordion-header" :id="`headingDetails-${image.filename}`">
                                        <button class="accordion-button collapsed" type="button"
                                            data-bs-toggle="collapse"
                                            :data-bs-target="`#collapseDetails-${image.filename}`" aria-expanded="false"
                                            :aria-controls="`collapseDetails-${image.filename}`">
                                            Quality {{ getDescription(image.filename)?.image_rank }}/10
                                        </button>
                                    </h2>
                                    <div :id="`collapseDetails-${image.filename}`" class="accordion-collapse collapse"
                                        :aria-labelledby="`headingDetails-${image.filename}`">
                                        <div class="accordion-body">

                                            <p class="card-text">
                                                <strong>The Photo:</strong>
                                                {{ getDescription(image.filename)?.summary || '' }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Delete Reason:</strong> {{
                                                    getDescription(image.filename)?.delete_reason || '' }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Scene:</strong> {{
                                                    getDescription(image.filename)?.scene || ''
                                                }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Setting:</strong> {{
                                                    getDescription(image.filename)?.setting || ''
                                                }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Text Content:</strong> {{
                                                    getDescription(image.filename)?.text_content || ''
                                                }}
                                            </p>
                                            <div v-if="getDescription(image.filename)?.objects?.length">
                                                <strong>Objects:</strong>
                                                <div>
                                                    <ul v-for="object in getDescription(image.filename).objects"
                                                        :key="object.name" class="list-group">
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

                    <h4>Prompt</h4>
                    <p>{{ prompt }}</p>

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
import { computed, ref, watch } from 'vue';
import { backendUrl } from '../config/backend_conf';
import criteriaData from '../config/criteria.json';
import promptsData from '../config/prompts.json';
import { ImageDescription } from '../data/ImageDescription';

const statusUrl = computed(() => `${backendUrl}/status`);
const processUrl = computed(() => `${backendUrl}/processtask`);
const imageDescriptions = ref<ImageDescription[]>([]); // Ensure descriptions include a "filename" property if available.
const loading = ref(false);
const error = ref('');
const imageInput = ref<HTMLInputElement | null>(null);
const images = ref<Array<{ filename: string; base64: string }>>([]);

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

// Helper: get the description matching the image's filename.
function getDescription(filename: string): any {
    return imageDescriptions.value.find(desc => desc.filename === filename);
}

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

            // Prepare description data (here, only the filename is provided)
            const descriptionPayload = new ImageDescription();
            descriptionPayload.filename = file.name;

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

            // Scale image for local preview
            const dataUrl = await scaleImageFile(file, 0.5);
            const base64Data = dataUrl.split(',')[1]; // Remove base64 prefix
            images.value.push({ filename: file.name, base64: base64Data });

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
        const id = Date.now();
        const filteredImages = images.value.filter(image =>
            !imageDescriptions.value.some(desc => desc.filename === image.filename)
        );
        if (filteredImages.length === 0) {
            loading.value = false;
            return;
        }
        // Only include criteria that are selected
        const selectedCriteria = criteria.value.filter(c => c.selected).map(c => c.text);
        const payload = {
            taskId: id,
            taskPrompt: prompt.value,
            criteria: selectedCriteria,
            images: filteredImages
        };
        const response = await axios.post(processUrl.value, payload);
        const data = response.data;
        if (data.status === "success" && id === data.taskId) {
            imageDescriptions.value = JSON.parse(data.result);
        } else {
            error.value = data.error;
        }
    } catch (err) {
        error.value = (err as Error).stack ? (err as Error).message : JSON.stringify(err);
    } finally {
        loading.value = false;
    }
};

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