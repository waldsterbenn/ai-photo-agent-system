<script setup lang="ts">
import { defineAsyncComponent, defineProps } from 'vue';
const DuplicateImages = defineAsyncComponent(() => import('./DuplicateImages.vue'));

const props = defineProps<{
    duplicateTimeThresholdMs: number;
}>();
</script>

<template>
    <Suspense>
        <template #default>
            <div class="content flex-grow-1 p-2 bg-secondary">
                <DuplicateImages :duplicateTimeThresholdMs="props.duplicateTimeThresholdMs" />
            </div>
        </template>
        <template #fallback>
            <div class="text-center">
                <div class="d-flex align-items-center">
                    <strong role="status">Searching for duplicates...</strong>
                    <div class="spinner-border ms-auto" aria-hidden="true"></div>
                </div>
            </div>
        </template>
    </Suspense>
</template>