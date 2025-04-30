<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
const DuplicateImages = defineAsyncComponent(() => import('./DuplicateImages.vue'));

</script>

<template>
    <Suspense>
        <template #default>
            <div class="content flex-grow-1 p-2 bg-secondary">
                <DuplicateImages />
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