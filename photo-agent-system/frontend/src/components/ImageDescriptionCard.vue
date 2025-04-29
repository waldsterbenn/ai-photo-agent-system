<script setup lang="ts">
import { ImageDescriptionViewModel } from '@/data/ImageDescriptionViewModel';
import { getBrowserLocale } from '@/utils/browserLocale';
import { getImageUrl } from '@/utils/getImageUrl';

const props = defineProps({
    imgDescVm: {
        type: ImageDescriptionViewModel,
        required: true
    }
})

const formatKey = (key: string) =>
    key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
</script>

<template>
    <div class="col">
        <div :class="`card h-100 ${imgDescVm.delete ? 'border border-danger' : ''}`">
            <div>
                <img v-if="imgDescVm.dummy"
                    :src="'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjwvc3ZnPg=='"
                    class="card-img-top img-thumbnail" alt="Image">
                <img v-else class="card-img-top img-thumbnail" :src="getImageUrl(imgDescVm.thumbnail_base64)"
                    alt="Image">
                <div v-if="imgDescVm.loading" class="spinner-overlay">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
            <button v-if="!imgDescVm.dummy" @click.stop="imgDescVm.delete = !imgDescVm.delete"
                class="btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2" title="Toggle delete">
                <i class="bi bi-x"></i>
            </button>
            <div v-if="!!imgDescVm.forencic_analysis" class="card-body text-start">
                <div class="card-title hstack gap-3 text-start">
                    <div class="card-text text-secondary text-truncate" :title="imgDescVm.filename">
                        {{ imgDescVm.filename }}
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
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                :data-bs-target="`#collapseDetails-${imgDescVm.filename}`" aria-expanded="false"
                                :aria-controls="`collapseDetails-${imgDescVm.filename}`">
                                Quality {{ imgDescVm.image_rank }}/10
                            </button>
                        </h2>
                        <div :id="`collapseDetails-${imgDescVm.filename}`" class="accordion-collapse collapse"
                            :aria-labelledby="`headingDetails-${imgDescVm.filename}`">
                            <div class="accordion-body">
                                <div class="card mt-2">
                                    <div class="card-body">
                                        <div class="card-text">
                                            <div
                                                v-if="imgDescVm?.metadata && Object.keys(imgDescVm.metadata).length > 0">
                                                <div class="col">
                                                    {{
                                                        new Date(imgDescVm?.metadata["exif"]["0th"]["DateTime"]
                                                            .replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
                                                            .replace(' ', 'T')).toLocaleString(getBrowserLocale()) || ''
                                                    }}
                                                </div>
                                                <div class="col badge">
                                                    {{
                                                        imgDescVm?.metadata["exif"]["0th"]["Make"] || ''
                                                    }}
                                                </div>
                                                <div v-if="imgDescVm?.size_uncompressed_mb" class="col badge">{{
                                                    imgDescVm?.size_uncompressed_mb }}Mb</div>
                                            </div>

                                            <div class="card-title mt-2">Photo:</div>
                                            <p class="card-text">
                                                {{ imgDescVm?.summary || '' }}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                <div class="card mt-2">
                                    <div class="card-body">
                                        <div v-if="imgDescVm?.delete_reason" class="card-text">
                                            <div class="card-title">
                                                Delete:
                                            </div> {{
                                                imgDescVm?.delete_reason || '' }}
                                        </div>
                                        <div v-if="imgDescVm?.keep_reason">
                                            <div class="card-title">
                                                Keep:
                                            </div>
                                            <div class="card-text">
                                                {{
                                                    imgDescVm?.keep_reason || ''
                                                }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <!-- <p v-if="imgDescVm?.scene" class="card-text">
                                    <strong>Scene:</strong> {{
                                        imgDescVm?.scene || ''
                                    }}
                                </p> -->
                                <!-- <p class="card-text">
                                    <strong>Setting:</strong> {{
                                        imgDescVm?.setting || ''
                                    }}
                                </p> -->
                                <div class="card mt-2" v-if="imgDescVm?.forencic_analysis">
                                    <div class="card-body">
                                        <div class="card-title">Analysis:</div>
                                        <p class="card-text">
                                            {{ imgDescVm?.forencic_analysis || '' }}
                                        </p>
                                    </div>
                                </div>
                                <div class="card mt-2" v-if="imgDescVm?.text_content">
                                    <div class="card-body">
                                        <div class="card-title">Text Content:</div>
                                        <p class="card-text">
                                            {{ imgDescVm?.text_content || '' }}
                                        </p>
                                    </div>
                                </div>

                                <div v-if="imgDescVm?.objects?.length" class="card mt-2">
                                    <div class="accordion" :id="`objectsAccordion-${imgDescVm.filename}`">
                                        <div class="accordion-item" v-for="(object, index) in imgDescVm.objects"
                                            :key="imgDescVm.filename + object.name + index">
                                            <h2 class="accordion-header">
                                                <button class="accordion-button collapsed" type="button"
                                                    data-bs-toggle="collapse"
                                                    :data-bs-target="`#accdn-${imgDescVm.filename}-${index}`"
                                                    aria-expanded="false"
                                                    :aria-controls="`accdn-${imgDescVm.filename}-${index}`">
                                                    {{ object.name }}
                                                </button>
                                            </h2>
                                            <div :id="`accdn-${imgDescVm.filename}-${index}`"
                                                class="accordion-collapse collapse"
                                                :data-bs-parent="`#objectsAccordion-${imgDescVm.filename}`">
                                                <div class="accordion-body">{{ object.attributes }}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div v-if="imgDescVm?.quality_criteria" class="card mt-2">
                                    <!-- <strong>Quality Checks:</strong> -->
                                    <div class="card-body">
                                        <div class="btn-group btn-group-sm" role="group">
                                            <div class="row">
                                                <button v-for="(value, key) in imgDescVm.quality_criteria" :key="key"
                                                    type="button"
                                                    :class="['col btn btn-sm m-1', value ? 'btn-secondary active' : 'btn-outline-secondary']">
                                                    {{ formatKey(key) }}
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="card-body text-start">
                <div class="card-title justify-content-between text-start">
                    <div class="vstack">
                        <div class="hstack gap-3">
                            <div class="card-text text-secondary text-truncate" :title="imgDescVm.filename">
                                {{ imgDescVm.filename }}
                            </div>
                            <div class="ms-auto">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" role="switch" value=""
                                        :id="`flexCheckDefault-${imgDescVm.filename}`" v-model="imgDescVm.delete">
                                    <label class="form-check-label" :for="`flexCheckDefault-${imgDescVm.filename}`">
                                        <i class="bi bi-trash"></i>
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="card-text text-secondary">
                            <div v-if="imgDescVm?.metadata && Object.keys(imgDescVm.metadata).length > 0"
                                class="card-text m-2">
                                {{ imgDescVm?.size_uncompressed_mb }}Mb

                                <div class="vr"></div>
                                {{
                                    new Date(imgDescVm?.metadata["exif"]["0th"]["DateTime"]
                                        .replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
                                        .replace(' ', 'T')).toLocaleString(getBrowserLocale()) || ''
                                }}
                                <div class="vr"></div>
                                {{
                                    imgDescVm?.metadata["exif"]["0th"]["Make"] || ''
                                }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
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