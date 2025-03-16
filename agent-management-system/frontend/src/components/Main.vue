<template>
    <div class="container-fluid d-flex flex-column h-100">
        <!-- Toolbar -->
        <div class="toolbar d-flex p-2 bg-light">
            <!-- Hidden File Input -->
            <input type="file" accept="image/*" multiple ref="imageInput" style="display:none"
                @change="handleImageUpload" />

            <!-- Button to trigger image picker -->
            <button @click="triggerImagePicker" class="btn btn-secondary me-2" title="Upload an image">
                <i class="bi bi-image"></i> Image
            </button>

            <!-- Send Message Button -->
            <button @click="sendMessage" class="btn btn-primary">Go</button>
        </div>
        <div class="d-flex flex-column">
            <h1>Image Analysis</h1>
            <p>{{ prompt }}</p>
            <p>{{ criteria }}</p>
        </div>
        <!-- Content area -->
        <div class="content flex-grow-1 p-2">
            <!-- <p>Backend URL: {{ statusUrl }}</p> -->
            <div v-if="images.length > 0" class="d-flex flex-column">
                <img v-for="(image, i) in images" :key="i" :src="getImageURL(image.base64)" class="img-thumbnail mt-2"
                    style="max-width: 80%; max-height: auto;" />

                <div v-for="(status, i) in imageDescriptions" :key="i" class="card mt-2">
                    <div class="card-body">
                        <h5 class="card-title">Image {{ i + 1 }}</h5>
                        <p class="card-text">{{ status.summary }}</p>
                        <p class="card-text">Scene: {{ status.scene }}</p>
                        <p class="card-text">Setting: {{ status.setting }}</p>
                        <p class="card-text">Text Content: {{ status.text_content }}</p>
                        <ul class="list-group
                            list-group-flush">
                            <li v-for="(object, j) in status.objects" :key="j" class="list-group-item">
                                <strong>{{ object.name }}</strong> - {{ object.attributes }}
                            </li>
                        </ul>
                        <p class="card-text">Delete: {{ status.delete }}</p>
                        <p class="card-text">Delete Reason: {{ status.delete_reason }}</p>
                        <p class="card-text">Image Rank: {{ status.image_rank }}</p>

                    </div>
                </div>
            </div>

            <p v-if="loading">Working...</p>
            <p v-else-if="error">{{ error }}</p>


        </div>
    </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { computed, ref } from 'vue';
import { backendUrl } from '../config/backend_conf';

const statusUrl = computed(() => `${backendUrl}/status`);
const processUrl = computed(() => `${backendUrl}/processtask`);
const imageDescriptions = ref<ImageDescription[]>();
const loading = ref(false);
const error = ref('');
const imageInput = ref<HTMLInputElement | null>(null);
const images = ref<[{}]>([]);
const taskPrompt = "Analyze the image and return a detailed JSON description including objects, scene, colors and any text detected. If you cannot determine certain details, leave those fields empty.";
const prompt = ref(taskPrompt);
const criteriaSingleImagePrompt = [
    "Rank the image and mark it to be deleted, if the image is raked below 5 or it meets any of the following criteria",
    //"Duplicated motif or scene.",
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
const sendMessage = async (e: Event) => {
    loading.value = true;
    const fake = {

        "result": "[{\"summary\": \"The image depicts two men standing near a stone wall with a blurred background of mountains and trees. The image quality is poor due to low resolution, blur, and potentially poor lighting.\", \"scene\": \"Outdoor, possibly a park or natural area with a stone wall.\", \"setting\": \"Landscape\", \"text_content\": \"\", \"objects\": [{\"name\": \"Man\", \"confidence\": 0.95, \"attributes\": \"Wearing a blue shirt, standing near a wall\"}, {\"name\": \"Man\", \"confidence\": 0.9, \"attributes\": \"Wearing a white shirt, standing near a wall\"}, {\"name\": \"Wall\", \"confidence\": 0.98, \"attributes\": \"Stone, appears old and weathered\"}, {\"name\": \"Tree\", \"confidence\": 0.75, \"attributes\": \"Green foliage, blurred\"}, {\"name\": \"Mountain\", \"confidence\": 0.6, \"attributes\": \"Blurred, distant\"}], \"delete\": false, \"delete_reason\": \"\", \"image_rank\": 3}, {\"summary\": \"The image appears to be a poorly composed shot of a stone wall with a blurred green background, likely a forest or foliage.\", \"scene\": \"Exterior, possibly a forest or wooded area.\", \"setting\": \"Outdoor\", \"text_content\": \"\", \"objects\": [{\"name\": \"Stone Wall\", \"confidence\": 0.95, \"attributes\": \"Rough, textured, gray, weathered\"}, {\"name\": \"Vegetation\", \"confidence\": 0.85, \"attributes\": \"Green, dense, blurred\"}, {\"name\": \"Background\", \"confidence\": 0.75, \"attributes\": \"Blurred, green\"}], \"delete\": true, \"delete_reason\": \"Low quality image. Obsured or unclear motifs. Poor composition or framing. Poor focus or sharpness. Poor lighting or exposure.\", \"image_rank\": 2}, {\"summary\": \"The image depicts two men standing near a stone wall with a blurred background of mountains and trees. The image quality is poor due to low resolution, blur, and potentially poor lighting.\", \"scene\": \"Outdoor, possibly a park or natural area with a stone wall.\", \"setting\": \"Landscape\", \"text_content\": \"\", \"objects\": [{\"name\": \"Man\", \"confidence\": 0.95, \"attributes\": \"Wearing a blue shirt, standing near a wall\"}, {\"name\": \"Man\", \"confidence\": 0.9, \"attributes\": \"Wearing a white shirt, standing near a wall\"}, {\"name\": \"Wall\", \"confidence\": 0.98, \"attributes\": \"Stone, appears old and weathered\"}, {\"name\": \"Tree\", \"confidence\": 0.75, \"attributes\": \"Green foliage, blurred\"}, {\"name\": \"Mountain\", \"confidence\": 0.6, \"attributes\": \"Blurred, distant\"}], \"delete\": false, \"delete_reason\": \"\", \"image_rank\": 3}, {\"summary\": \"The image appears to be a poorly composed shot of a stone wall with a blurred green background, likely a forest or foliage.\", \"scene\": \"Exterior, possibly a forest or wooded area.\", \"setting\": \"Outdoor\", \"text_content\": \"\", \"objects\": [{\"name\": \"Stone Wall\", \"confidence\": 0.95, \"attributes\": \"Rough, textured, gray, weathered\"}, {\"name\": \"Vegetation\", \"confidence\": 0.85, \"attributes\": \"Green, dense, blurred\"}, {\"name\": \"Background\", \"confidence\": 0.75, \"attributes\": \"Blurred, green\"}], \"delete\": true, \"delete_reason\": \"Low quality image. Obsured or unclear motifs. Poor composition or framing. Poor focus or sharpness. Poor lighting or exposure.\", \"image_rank\": 2}]",
        "status": "success",
        "taskId": 1742144313254
    };
    console.log(fake.result);
    const newLocal: ImageDescription[] = JSON.parse(fake.result);
    imageDescriptions.value = newLocal;
    return;
    try {

        const payload = { taskId: Date.now(), taskPrompt: taskPrompt, criteria: criteriaSingleImagePrompt, images: images.value };
        const response = await axios.post(processUrl.value, payload);
        imageDescriptions.value = JSON.parse(response.data) as ImageDescription[];
        //status.value = JSON.stringify();
    } catch (err) {
        error.value = (err as Error).message;
    } finally {
        loading.value = false;
    }
};

function triggerImagePicker() {
    imageInput.value?.click();
}

function getImageURL(image: string): string {
    if (image.startsWith('data:')) return image;
    return `data:image/png;base64,${image}`;
}

async function resizeImageFile(file: File, maxWidth: number = 800): Promise<string> {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
            // Calculate scale factor to maintain aspect ratio.
            const scale = Math.min(maxWidth / img.width, maxWidth / img.height);
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
            const dataUrl = await resizeImageFile(file, 1024);
            const base64Data = dataUrl.split(',')[1]; // Remove base64 prefix
            images.value.push({ filename: "" + file.name, base64: base64Data });
        } catch (error) {
            console.error("Image upload error:", error);
            error.value = (error as Error).message;
        }
    }
    target.value = "";
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

// onMounted(() => {
//     fetchStatus();
// });
</script>

<style scoped>
h1 {
    font-size: 24px;
    margin-bottom: 20px;
}
</style>