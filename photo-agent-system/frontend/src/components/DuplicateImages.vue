<script setup lang="ts">

import { DuplicateFinder, DuplicationCluster } from '@/tools/DuplicateFinder';
import { getBrowserLocale } from '@/utils/browserLocale';
import { getImageUrl } from '@/utils/getImageUrl';
import { ref } from 'vue';

class DuplicationGroupDto {
    filenames: string[] = [];
    reason: string = '';
    group_header: string = '';
}
class DuplicationAnalysisResultDto {
    analisys_summary: string = '';
    duplicate_groups: DuplicationGroupDto[] = [];
}

interface Props {
}
const props = defineProps<Props>();

import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionDto } from '@/data/ImageDescriptionDto';
import { useImageDescriptionsStore } from '@/stores/imageDescriptionsStore';
import axios from 'axios';
const imageDescriptionsStore = useImageDescriptionsStore();

const duplicateClusters = ref<DuplicationCluster[]>([]);
const aiDetectionSummary = ref("");
const analysing = ref(false);

//await new Promise(resolve => setTimeout(resolve, 5000)); // Simulate a delay for the sake of example

duplicateClusters.value = new DuplicateFinder().findDuplicates(imageDescriptionsStore.imageDescriptions);


const detectWithAi = async () => {
    analysing.value = true;
    const dtos = imageDescriptionsStore.imageDescriptions
        .filter(x => !!x.forencic_analysis)
        .map(x => Object.assign(new ImageDescriptionDto(), x));
    dtos.forEach(x => {
        x.thumbnail_base64 = "";
    });
    const taskId = Date.now();
    const payload = {
        taskId: taskId,
        imageDescriptions: dtos
    };

    try {
        const response = await axios.post(`${backendUrl}/duplicate-detection`, payload);
        const groups: DuplicationAnalysisResultDto = Object.assign(new DuplicationAnalysisResultDto(), response.data.result);
        //         const response = JSON.parse(`{
        //     "analysis_summary": "Two potential duplicate image descriptions were identified, depicting similar scenes of a red train at a station platform.",
        //     "duplicate_groups": [
        //         {
        //             "filenames": [
        //                 "20250413_110512.jpg",
        //                 "20250413_110520.jpg"
        //             ],
        //             "reason": "Both images describe a red train with a black front or gray accents stopped at a station platform, with a similar setting of a train station."
        //         }
        //     ]
        // }`);
        //         const groups = Object.assign(new DuplicationAnalysisResultDto(), response);

        aiDetectionSummary.value = groups.analisys_summary;
        // Create clusters based on duplicate_groups without using flatMap.
        const clustersFromAi = groups.duplicate_groups
            .map(dupGroup => {
                // Map filenames to image descriptions from the store.
                const images = dupGroup.filenames
                    .map(filename => imageDescriptionsStore.imageDescriptions.find(img => img.filename === filename))
                    .filter(img => !!img);
                if (images.length) {
                    return {
                        groupId: images.map(x => x.filename).join(","),
                        groupHeader: dupGroup.group_header,
                        images: images,
                        reason: dupGroup.reason,
                        time: undefined,
                        typeIcon: 'bi-robot'
                    } as DuplicationCluster;
                }
                return null;
            });

        clustersFromAi.forEach(cluster => {
            if (cluster && !duplicateClusters.value.some(c => c.groupId === cluster.groupId)) {
                duplicateClusters.value.push(cluster);
            }
        });
    } catch (error) {
        console.error('Error during duplicate detection:', error);
        throw error;
    }
    analysing.value = false;
};
</script>

<template>
    <div>
        <button @click="detectWithAi" class="btn btn-primary m-2" :disabled="analysing"
            title="Detect duplicates with AI">
            <span v-if="analysing" class="spinner-border spinner-border-sm me-2" title="Working" role="status"
                aria-hidden="true"></span>
            <i class="bi bi-robot"></i> Detect Duplicates with AI
        </button>
        {{ aiDetectionSummary }}
        <div v-if="duplicateClusters && duplicateClusters.length" class="container">
            <div class="row">
                <div v-for="cluster in duplicateClusters" :key="cluster.time ?? cluster.groupId"
                    class="col-12 col-sm-12 col-md-10 col-lg-6 col-xl-4 g-2">
                    <div class="card">
                        <div v-if="cluster.time" class="row row-cols-auto card-header"
                            title="Photos taken in close succession">
                            <i class="col bi bi-clock"></i>
                            <span clas="col">{{ new
                                Date(cluster.time).toLocaleString(getBrowserLocale()) }}
                            </span>
                        </div>
                        <div v-else class="row row-cols-auto card-header" title="AI thinks these photos are duplicates">
                            <i class="col bi bi-robot"></i>
                            <span clas="col ms-auto">
                                {{ cluster.groupHeader }}
                            </span>
                        </div>
                        <div class="card-body">
                            <div class="row row-cols-2 g-3">
                                <div class="card col" v-for="imgDesc in cluster.images" :key="imgDesc.filename">
                                    <div :class="[imgDesc.delete ? 'border border-danger' : '']">
                                        <img :src="getImageUrl(imgDesc.thumbnail_base64)"
                                            class="card-img-top img-thumbnail" alt="Image">
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
                        <div v-if="cluster.reason" class="card-footer text-muted">
                            <p class="card-text">{{ cluster.reason }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else class="alert alert-info" role="alert">
            No duplicate images found.
        </div>
    </div>
</template>

<style scoped lang="css"></style>