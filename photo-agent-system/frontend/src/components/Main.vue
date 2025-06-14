<script setup lang="ts">
import { fetchImageDescriptions as fetchApiImageDescriptions } from '@/api/imageDescriptionsApi';
import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { useAppStateStore } from '@/stores/appStateStore';
import { useImageDescriptionsStore } from '@/stores/imageDescriptionsStore';
import { useToolbarStore } from '@/stores/toolbarStore';
import axios from 'axios';
import { computed, onMounted } from 'vue';
import AnalysisModal from './AnalysisModal.vue';
import AppStatusPanel from './AppStatusPanel.vue';
import DuplicateImagesSuspense from './DuplicateImagesSuspense.vue';
import ImageDescriptionCard from './ImageDescriptionCard.vue';
import Toolbar from './Toolbar.vue';

const toolbarStore = useToolbarStore();
const imageDescriptionsStore = useImageDescriptionsStore();
const appStateStore = useAppStateStore();

const columnsClass = computed(() => {
    if (appStateStore.analysisModal.columnsCount) {
        return `row row-cols-${appStateStore.analysisModal.columnsCount} g-2`;
    }
    //Adaptive columns for different screen sizes, in auto mode
    return "row row-cols-1 row-cols-sm-1 row-cols-md-2 row-cols-lg-2 row-cols-xl-3 g-2";
});

async function makePlaceholderDescriptions() {
    console.log("Counting image descriptions...");
    try {
        const count = await axios.get(`${backendUrl}/image-descriptions-count`);
        if (count.data === 0) {
            return;
        }
        const range = Array.from({ length: count.data }, (_, i) => i);
        const dummies = range.map((i) => ({
            id: i,
            dummy: true,
            loading: true,
        } as ImageDescriptionViewModel));
        imageDescriptionsStore.setImageDescriptions(dummies);
    } catch (err) {
        console.error("Error counting image descriptions:", err);
        appStateStore.error = (err as Error).message || JSON.stringify(err);
    }
}

onMounted(() => {
    makePlaceholderDescriptions();
    fetchApiImageDescriptions();
});

</script>

<template>
    <div class="container-fluid d-flex flex-column h-100 bg-secondary-subtle">
        <Toolbar />

        <DuplicateImagesSuspense v-if="toolbarStore.searchForDuplicates" />

        <div class="content flex-grow-1 p-2">
            <AppStatusPanel />

            <div v-if="imageDescriptionsStore.imageDescriptions.length > 0" :class="columnsClass">
                <ImageDescriptionCard v-for="imgDescVm in imageDescriptionsStore.imageDescriptions" :key="imgDescVm.id"
                    :imgDescVm="imgDescVm" />
            </div>
        </div>
    </div>

    <AnalysisModal />
</template>

<style scoped lang="css"></style>