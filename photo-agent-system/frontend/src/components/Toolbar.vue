<template>
    <div class="toolbar d-flex p-2 bg-secondary-subtle sticky-top hstack gap-3">
        <!-- Hidden File Input -->
        <input type="file" accept="image/*" multiple ref="imageInput" style="display:none"
            @change="$emit(EVENT_HANDLE_IMAGE_UPLOAD, $event)" />

        <!-- Gear icon button to open analysis modal -->
        <button @click="$emit(EVENT_OPEN_ANALYSIS_MODAL)" class="btn btn-secondary-subtle p-2"
            title="Analysis Settings">
            <i class="bi bi-gear"></i>
        </button>

        <!-- Button to trigger image picker -->
        <button @click="$emit(EVENT_TRIGGER_IMAGE_PICKER)" class="btn btn-secondary p-2 ms-auto" title="Upload a photo">
            <i class="bi bi-image"></i> Select Photos
        </button>

        <input type="checkbox" class="btn-check" id="btn-check-duplicates" autocomplete="off"
            v-model="searchForDuplicates" @click="$emit(EVENT_FIND_DUPLICATES)" />
        <label class="btn btn-secondary p-2" for="btn-check-duplicates">
            Duplicates <i class="bi bi-copy"></i>
        </label>

        <button @click="" class="btn btn-secondary p-2 disabled" title="Sort">
            <i class="bi bi-sort-alpha-down"></i> Sort
        </button>

        <div class="vr"></div>

        <!-- Button to delete photos -->
        <button @click="$emit(EVENT_DELETE_SELECTED)" class="btn btn-secondary p-2" title="Delete selected photos">
            <i class="bi bi-trash"></i>
        </button>

        <!-- Send Message Button -->
        <button @click="$emit(EVENT_SEND_MESSAGE)" class="btn btn-primary p-2" :disabled="loading">Go</button>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Define constants for event names to avoid magic strings
export const EVENT_HANDLE_IMAGE_UPLOAD = 'handleImageUpload';
export const EVENT_OPEN_ANALYSIS_MODAL = 'openAnalysisModal';
export const EVENT_TRIGGER_IMAGE_PICKER = 'triggerImagePicker';
export const EVENT_FIND_DUPLICATES = 'findDuplicates';
export const EVENT_DELETE_SELECTED = 'deleteSelected';
export const EVENT_SEND_MESSAGE = 'sendMessage';

const searchForDuplicates = ref(false);
const loading = ref(false);
</script>

<style scoped>
.vr {
    border-left: 1px solid #dee2e6;
    height: 100%;
    margin: 0 1rem;
}
</style>