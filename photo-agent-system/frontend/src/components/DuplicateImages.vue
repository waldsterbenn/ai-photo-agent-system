<script setup lang="ts">

import { DuplicateFinder } from '@/tools/DuplicateFinder';
import { getBrowserLocale } from '@/utils/browserLocale';
import { getImageURL } from '@/utils/getImageURL';
import { computed } from 'vue';

interface Props {
    duplicateTimeThresholdMs?: number;
}
const props = defineProps<Props>();

import { useImageDescriptionsStore } from '@/stores/imageDescriptionsStore';
const imageDescriptionsStore = useImageDescriptionsStore();

//await new Promise(resolve => setTimeout(resolve, 5000)); // Simulate a delay for the sake of example
const duplicateClusters = computed(() => {
    return new DuplicateFinder(props.duplicateTimeThresholdMs).findDuplicates(imageDescriptionsStore.imageDescriptions);
});
</script>

<template>
    <div v-if="duplicateClusters.length">
        <div v-for="cluster in duplicateClusters" :key="cluster.time" class="row">
            <div class="col m-2">
                <div class="card text-center">
                    <div class="card-header">
                        Duplicates ({{ new Date(cluster.time).toLocaleString(getBrowserLocale()) }})
                    </div>
                    <div class="hstack">
                        <div class="m-2" v-for="imgDesc in cluster.images" :key="imgDesc.filename">
                            <div :class="`card ${imgDesc.delete ? 'border border-danger' : ''}`">
                                <img :src="getImageURL(imgDesc.thumbnail_base64)" class="card-img-top img-thumbnail"
                                    alt="Image">
                                <button @click.stop="imgDesc.delete = !imgDesc.delete"
                                    class="btn btn-sm btn-primary m-2" title="Toggle delete">
                                    <i class="bi bi-trash"></i>
                                </button>
                                <div class="card-body">
                                    <p class="card-text">{{ imgDesc.filename }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div v-else class="alert" role="alert">
        No duplicate images found.
    </div>
</template>

<style scoped lang="css">
/* ...existing styles if needed... */
</style>