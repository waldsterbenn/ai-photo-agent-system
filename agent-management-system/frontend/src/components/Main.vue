<template>
    <div class="container-fluid d-flex flex-column h-100">
        <div class="accordion mt-3">
            <div class="accordion-item">
                <h2 class="accordion-header" :id="`analysisDetailsHeading`">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                        :data-bs-target="`#analysisDetails`" aria-expanded="false" :aria-controls="`analysisDetails`">
                        Analysis information
                    </button>
                </h2>
                <div :id="`analysisDetails`" class="accordion-collapse collapse"
                    :aria-labelledby="`analysisDetailsHeading`">
                    <div class="accordion-body">

                        <h1>Image Analysis</h1>
                        <p>{{ prompt }}</p>
                        <p>{{ criteria }}</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- Toolbar -->
        <div class="toolbar d-flex p-2 bg-light">
            <!-- Hidden File Input -->
            <input type="file" accept="image/*" multiple ref="imageInput" style="display:none"
                @change="handleImageUpload" />

            <!-- Button to trigger image picker -->
            <button @click="triggerImagePicker" class="btn btn-secondary me-2" title="Upload an image">
                <i class="bi bi-image"></i> Select Photos
            </button>

            <!-- Send Message Button -->
            <button @click="sendMessage" class="btn btn-primary">Go</button>
        </div>

        <!-- Content area -->
        <div class="content flex-grow-1 p-2">
            <p v-if="loading">Working...</p>
            <p v-else-if="error">{{ error }}</p>

            <div v-if="images.length > 0" class="row">
                <div class="col-md-4 mb-3" v-for="image in images" :key="image.filename">
                    <div class="card h-100 text-start">
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
                                                    getDescription(image.filename)?.setting ||
                                                    '' }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Text Content:</strong> {{
                                                    getDescription(image.filename)?.text_content || '' }}
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
</template>

<script setup lang="ts">
import axios from 'axios';
import { computed, ref } from 'vue';
import { backendUrl } from '../config/backend_conf';

const statusUrl = computed(() => `${backendUrl}/status`);
const processUrl = computed(() => `${backendUrl}/processtask`);
const imageDescriptions = ref<any[]>([]); // Ensure descriptions include a "filename" property if available.
const loading = ref(false);
const error = ref('');
const imageInput = ref<HTMLInputElement | null>(null);
const images = ref<Array<{ filename: string; base64: string }>>([]);
const taskPrompt = "Analyze the image and return a detailed JSON description including objects, scene, colors and any text detected. If you cannot determine certain details, leave those fields empty.";
const prompt = ref(taskPrompt);
const criteriaSingleImagePrompt = [
    "Rank the image and mark it to be deleted, if the image is raked below 5 or it meets any of the following criteria",
    "Low quality image.",
    "Obscured or unclear motifs.",
    "Poor lighting or exposure.",
    "Poor composition or framing.",
    "Irrelevant or uninteresting content.",
    "Poor focus or sharpness.",
    "Poor color balance or saturation.",
    "Excessive noise or artifacts.",
    "Closed eyes or unflattering facial expressions.",
    "Finger or hand covering the lens.",
    "Overexposed or underexposed.",
];
const criteria = ref(criteriaSingleImagePrompt);

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

async function resizeImageFile(file: File, scaleFactor: number = 0): Promise<string> {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
            // Calculate scale factor to maintain aspect ratio.
            let scale;
            if (scaleFactor === 0)
                scale = 1;
            else
                scale = Math.min(scaleFactor / img.width, scaleFactor / img.height);
            const width = img.width * scale;
            const height = img.height * scale;

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
            const dataUrl = await resizeImageFile(file);
            const base64Data = dataUrl.split(',')[1]; // Remove base64 prefix
            images.value.push({ filename: "" + file.name, base64: base64Data });
        } catch (error) {
            console.error("Image upload error:", error);
            error.value = (error as Error).message;
        }
    }
    target.value = "";
}

const sendMessage = async (e: Event) => {
    loading.value = true;
    error.value = "";
    // const fake = {

    //     "result": "[{\"summary\": \"The image depicts two men standing near a stone wall with a blurred background of mountains and trees. The image quality is poor due to low resolution, blur, and potentially poor lighting.\", \"scene\": \"Outdoor, possibly a park or natural area with a stone wall.\", \"setting\": \"Landscape\", \"text_content\": \"\", \"objects\": [{\"name\": \"Man\", \"confidence\": 0.95, \"attributes\": \"Wearing a blue shirt, standing near a wall\"}, {\"name\": \"Man\", \"confidence\": 0.9, \"attributes\": \"Wearing a white shirt, standing near a wall\"}, {\"name\": \"Wall\", \"confidence\": 0.98, \"attributes\": \"Stone, appears old and weathered\"}, {\"name\": \"Tree\", \"confidence\": 0.75, \"attributes\": \"Green foliage, blurred\"}, {\"name\": \"Mountain\", \"confidence\": 0.6, \"attributes\": \"Blurred, distant\"}], \"delete\": false, \"delete_reason\": \"\", \"image_rank\": 3}, {\"summary\": \"The image appears to be a poorly composed shot of a stone wall with a blurred green background, likely a forest or foliage.\", \"scene\": \"Exterior, possibly a forest or wooded area.\", \"setting\": \"Outdoor\", \"text_content\": \"\", \"objects\": [{\"name\": \"Stone Wall\", \"confidence\": 0.95, \"attributes\": \"Rough, textured, gray, weathered\"}, {\"name\": \"Vegetation\", \"confidence\": 0.85, \"attributes\": \"Green, dense, blurred\"}, {\"name\": \"Background\", \"confidence\": 0.75, \"attributes\": \"Blurred, green\"}], \"delete\": true, \"delete_reason\": \"Low quality image. Obsured or unclear motifs. Poor composition or framing. Poor focus or sharpness. Poor lighting or exposure.\", \"image_rank\": 2}, {\"summary\": \"The image depicts two men standing near a stone wall with a blurred background of mountains and trees. The image quality is poor due to low resolution, blur, and potentially poor lighting.\", \"scene\": \"Outdoor, possibly a park or natural area with a stone wall.\", \"setting\": \"Landscape\", \"text_content\": \"\", \"objects\": [{\"name\": \"Man\", \"confidence\": 0.95, \"attributes\": \"Wearing a blue shirt, standing near a wall\"}, {\"name\": \"Man\", \"confidence\": 0.9, \"attributes\": \"Wearing a white shirt, standing near a wall\"}, {\"name\": \"Wall\", \"confidence\": 0.98, \"attributes\": \"Stone, appears old and weathered\"}, {\"name\": \"Tree\", \"confidence\": 0.75, \"attributes\": \"Green foliage, blurred\"}, {\"name\": \"Mountain\", \"confidence\": 0.6, \"attributes\": \"Blurred, distant\"}], \"delete\": false, \"delete_reason\": \"\", \"image_rank\": 3}, {\"summary\": \"The image appears to be a poorly composed shot of a stone wall with a blurred green background, likely a forest or foliage.\", \"scene\": \"Exterior, possibly a forest or wooded area.\", \"setting\": \"Outdoor\", \"text_content\": \"\", \"objects\": [{\"name\": \"Stone Wall\", \"confidence\": 0.95, \"attributes\": \"Rough, textured, gray, weathered\"}, {\"name\": \"Vegetation\", \"confidence\": 0.85, \"attributes\": \"Green, dense, blurred\"}, {\"name\": \"Background\", \"confidence\": 0.75, \"attributes\": \"Blurred, green\"}], \"delete\": true, \"delete_reason\": \"Low quality image. Obsured or unclear motifs. Poor composition or framing. Poor focus or sharpness. Poor lighting or exposure.\", \"image_rank\": 2, \"filename\": \"DSC00067.JPG\"}]",
    //     "status": "success",
    //     "taskId": 1742144313254
    // };
    // console.log(fake.result);
    // const newLocal: any[] = JSON.parse(fake.result);
    // imageDescriptions.value = newLocal;
    // return;
    try {

        const id = Date.now();
        const payload = { taskId: id, taskPrompt: taskPrompt, criteria: criteriaSingleImagePrompt, images: images.value };
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

// onMounted(() => {
//     fetchStatus();
// });
function updateDeleteStatus(filename: string, value: boolean) {
    const description = getDescription(filename);
    if (description) {
        description.delete = value;
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