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

        <!-- Content area -->
        <div class="content flex-grow-1 p-2">
            <!-- <p>Backend URL: {{ statusUrl }}</p> -->
            <div v-if="images.length > 0" class="d-flex flex-column">
                <img v-for="(image, i) in images" :key="i" :src="getImageURL(image.base64)" class="img-thumbnail mt-2"
                    style="max-width: 80%; max-height: auto;" />
            </div>

            <p v-if="loading">Working...</p>
            <p v-else-if="error">{{ error }}</p>
            <p v-else>{{ status }}</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { computed, ref } from 'vue';
import { backendUrl } from '../config/backend_conf';

const statusUrl = computed(() => `${backendUrl}/status`);
const processUrl = computed(() => `${backendUrl}/processtask`);
const status = ref('');
const loading = ref(false);
const error = ref('');
const imageInput = ref<HTMLInputElement | null>(null);
const images = ref<[{}]>([]);

const sendMessage = async (e: Event) => {
    loading.value = true;
    try {
        // Wrap the data in a 'task' property as expected by the server
        const payload = images.value;
        const response = await axios.post(processUrl.value, payload);
        status.value = JSON.stringify(response.data);
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
        status.value = JSON.stringify(response.data);
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