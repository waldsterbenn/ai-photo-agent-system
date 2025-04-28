<script setup lang="ts">
import { fetchImageDescriptions as fetchApiImageDescriptions } from '@/api/imageDescriptionsApi';
import { backendUrl } from '@/config/backend_conf';
import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { useAppStateStore } from '@/stores/appStateStore';
import { useImageDescriptionsStore } from '@/stores/imageDescriptionsStore';
import { useToolbarStore } from '@/stores/toolbarStore';
import { getBrowserLocale } from '@/utils/browserLocale';
import { getImageURL } from '@/utils/getImageUrl';
import axios from 'axios';
import { onMounted } from 'vue';
import AnalysisModal from './AnalysisModal.vue';
import AppStatusPanel from './AppStatusPanel.vue';
import DuplicateImagesSuspense from './DuplicateImagesSuspense.vue';
import Toolbar from './Toolbar.vue';

const toolbarStore = useToolbarStore();
const imageDescriptionsStore = useImageDescriptionsStore();
const appStateStore = useAppStateStore();

const duplicateTimeThresholdMs = 10 * 1000;

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
        <!-- Toolbar -->
        <Toolbar />
        <div>
            <DuplicateImagesSuspense v-if="toolbarStore.searchForDuplicates"
                :duplicateTimeThresholdMs="duplicateTimeThresholdMs" />
        </div>
        <div class="hr"></div>
        <!-- Content area -->
        <div class="content flex-grow-1 p-2">
            <AppStatusPanel />
            <div v-if="imageDescriptionsStore.imageDescriptions.length > 0"
                :class="`row row-cols-${appStateStore.analysisModal.columnsCount} g-3`">
                <div class="col" v-for="imgDescVm in imageDescriptionsStore.imageDescriptions" :key="imgDescVm.id">
                    <div
                        :class="`card h-100 text-center position-relative ${imgDescVm.delete ? 'border border-danger' : ''}`">

                        <div class="position-relative">
                            <img v-if="imgDescVm.dummy"
                                :src="'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjwvc3ZnPg=='"
                                class="card-img-top img-thumbnail" alt="Image">
                            <img v-else :src="getImageURL(imgDescVm.thumbnail_base64)"
                                class="card-img-top img-thumbnail" alt="Image">

                            <div v-if="imgDescVm.loading" class="spinner-overlay">
                                <div class="spinner-border" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>

                        </div>
                        <button v-if="!imgDescVm.dummy" @click.stop="imgDescVm.delete = !imgDescVm.delete"
                            class="btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2"
                            title="Toggle delete">
                            <i class="bi bi-x"></i>
                        </button>
                        <div v-if="!!imgDescVm.scene" class="card-body">
                            <div class="card-title align-items-center hstack gap-3">
                                <div class="card-text text-secondary text-truncate" :title="imgDescVm.filename">
                                    {{
                                        imgDescVm.filename }}
                                </div>
                                <div class="form-check form-switch ms-auto">
                                    <input class="form-check-input" type="checkbox" role="switch" value=""
                                        :id="`flexCheckDefault-${imgDescVm.filename}`" v-model="imgDescVm.delete">
                                    <label class="form-check-label" :for="`flexCheckDefault-${imgDescVm.filename}`">
                                        <i class="bi bi-trash"></i>
                                    </label>
                                </div>
                            </div>
                            <div class="accordion mt-3" :id="`accordionDetails-${imgDescVm.filename}`">
                                <div class="accordion-item">
                                    <h2 class="accordion-header" :id="`headingDetails-${imgDescVm.filename}`">
                                        <button class="accordion-button collapsed" type="button"
                                            data-bs-toggle="collapse"
                                            :data-bs-target="`#collapseDetails-${imgDescVm.filename}`"
                                            aria-expanded="false"
                                            :aria-controls="`collapseDetails-${imgDescVm.filename}`">
                                            Quality {{ imgDescVm.image_rank }}/10
                                        </button>
                                    </h2>
                                    <div :id="`collapseDetails-${imgDescVm.filename}`"
                                        class="accordion-collapse collapse"
                                        :aria-labelledby="`headingDetails-${imgDescVm.filename}`">
                                        <div class="accordion-body">

                                            <div v-if="imgDescVm?.metadata && Object.keys(imgDescVm.metadata).length > 0"
                                                class="card-text">
                                                {{
                                                    imgDescVm?.metadata["exif"]["0th"]["Make"] || ''
                                                }}
                                                <div class="vr"></div>
                                                {{
                                                    new Date(imgDescVm?.metadata["exif"]["0th"]["DateTime"]
                                                        .replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
                                                        .replace(' ', 'T')).toLocaleString(getBrowserLocale()) || ''
                                                }}
                                                <!-- {{ imgDesc?.metadata }} -->
                                            </div>

                                            <p class="card-text">
                                                <strong>Photo:</strong>
                                                {{ imgDescVm?.summary || '' }}
                                            </p>

                                            <p v-if="imgDescVm?.delete_reason" class="card-text">
                                                <strong>Delete:</strong> {{
                                                    imgDescVm?.delete_reason || '' }}
                                            </p>

                                            <p v-if="imgDescVm?.keep_reason" class="card-text">
                                                <strong>Keep:</strong> {{
                                                    imgDescVm?.keep_reason || ''
                                                }}
                                            </p>
                                            <p v-if="imgDescVm?.scene" class="card-text">
                                                <strong>Scene:</strong> {{
                                                    imgDescVm?.scene || ''
                                                }}
                                            </p>
                                            <p class="card-text">
                                                <strong>Setting:</strong> {{
                                                    imgDescVm?.setting || ''
                                                }}
                                            </p>
                                            <p v-if="imgDescVm?.text_content" class="card-text">
                                                <strong>Text Content:</strong> {{
                                                    imgDescVm?.text_content || ''
                                                }}
                                            </p>

                                            <p v-if="imgDescVm?.forencic_analysis" class="card-text">
                                                <strong>Analysis:</strong> {{
                                                    imgDescVm?.forencic_analysis || ''
                                                }}
                                            </p>

                                            <div v-if="imgDescVm?.objects?.length">
                                                <strong>Objects:</strong>
                                                <div>
                                                    <ul v-for="object in imgDescVm.objects" :key="object.name"
                                                        class="list-group">
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

                                            <p v-if="imgDescVm?.quality_criteria" class="card-text">
                                                <strong>Quality Checks:</strong> {{
                                                    imgDescVm?.quality_criteria || ''
                                                }}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="card-body">
                            <div class="card-title d-flex justify-content-between align-items-center">
                                <div class="vstack">
                                    <div class="hstack">
                                        <div class="p-2  ms-auto">
                                            <div class="form-check form-switch">
                                                <input class="form-check-input" type="checkbox" role="switch" value=""
                                                    :id="`flexCheckDefault-${imgDescVm.filename}`"
                                                    v-model="imgDescVm.delete">
                                                <label class="form-check-label"
                                                    :for="`flexCheckDefault-${imgDescVm.filename}`">
                                                    <i class="bi bi-trash"></i>
                                                </label>

                                            </div>
                                        </div>
                                    </div>
                                    <div class="card-text">
                                        <div class="card-text text-secondary">{{ imgDescVm.filename }}</div>
                                        <div v-if="imgDescVm?.metadata && Object.keys(imgDescVm.metadata).length > 0"
                                            class="card-text text-secondary">
                                            {{
                                                new Date(imgDescVm?.metadata["exif"]["0th"]["DateTime"]
                                                    .replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
                                                    .replace(' ', 'T')).toLocaleString(getBrowserLocale()) || ''
                                            }}
                                            <div class="vr"></div>
                                            {{
                                                imgDescVm?.metadata["exif"]["0th"]["Make"] || ''
                                            }}

                                            <!-- {{ imgDesc?.metadata }} -->
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

    <AnalysisModal />
</template>

<style scoped lang="css">
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