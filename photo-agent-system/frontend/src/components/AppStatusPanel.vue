<script setup lang="ts">
import { useAppStateStore } from '@/stores/appStateStore';
const appStateStore = useAppStateStore();

function clearError() {
    appStateStore.error = undefined;
}
</script>

<template>
    <div v-if="appStateStore.loading || !!appStateStore.error" class="content flex-grow-1 p-2">
        <div class="text-center">
            <div class="d-flex align-items-center justify-content-center">
                <p v-if="appStateStore.loading">Working...</p>
            </div>
            <div class="mt-2" v-if="appStateStore.error">
                <div class="panel alert alert-danger alert-dismissible fade show">
                    <div class="d-flex justify-content-between align-items-center">
                        <p class="mb-0">{{ appStateStore.error }}</p>
                        <button type="button" class="btn-close" aria-label="Close" @click="clearError"></button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>