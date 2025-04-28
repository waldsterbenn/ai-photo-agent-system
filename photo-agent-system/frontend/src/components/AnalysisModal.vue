<script setup lang="ts">
import { useAppStateStore } from '@/stores/appStateStore';
import { watch, computed } from 'vue';

const appStateStore = useAppStateStore();

// Watch selectedPromptId so that the prompt value can be updated when a new selection is made
watch(() => appStateStore.analysisModal.selectedPromptId, () => {
    appStateStore.updatePrompt();
});

// Computed property to convert the prompt array to a newline-delimited string and vice versa
const promptText = computed({
    get() {
        const prompt = appStateStore.analysisModal.prompt;
        return Array.isArray(prompt) ? prompt.join("\n") : prompt;
    },
    set(val: string) {
        appStateStore.analysisModal.prompt = val.split("\n");
    }
});
</script>

<template>
    <!-- Analysis Modal -->
    <div class="modal fade" id="analysisModal" tabindex="-1" aria-labelledby="analysisModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="analysisModalLabel">Configuration</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <h4>Profile</h4>
                            <select class="form-select" v-model.number="appStateStore.analysisModal.selectedPromptId">
                                <option v-for="p in appStateStore.analysisModal.promptsOptions" :key="p.id"
                                    :value="p.id">
                                    {{ p.name }}
                                </option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <h4>Card Columns</h4>
                            <div class="btn-group flex-wrap">
                                <button type="button" v-for="n in [1, 2, 3, 4, 5]" :key="n" class="btn" :class="{
                                    'btn-primary': appStateStore.analysisModal.columnsCount === n,
                                    'btn-outline-primary': appStateStore.analysisModal.columnsCount !== n
                                }" @click="appStateStore.analysisModal.columnsCount = n">
                                    {{ n }}
                                </button>
                            </div>
                        </div>
                    </div>

                    <h4>Prompt</h4>
                    <textarea class="form-control mb-3" rows="6" v-model="promptText"></textarea>

                    <h4>Deletion criteria</h4>
                    <div class="btn-group flex-wrap" role="group" aria-label="Deletion criteria">
                        <button type="button" v-for="(crit, index) in appStateStore.analysisModal.criteria" :key="index"
                            class="btn m-1"
                            :class="{ 'btn-primary': crit.selected, 'btn-outline-primary': !crit.selected }"
                            @click="crit.selected = !crit.selected">
                            {{ crit.text }}
                        </button>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Ok</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="css">
/* No custom CSS required */
</style>