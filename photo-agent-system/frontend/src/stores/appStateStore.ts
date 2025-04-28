import * as criteriaData from '@/config/criteria.json';
import * as promptsData from '@/config/prompts.json';
import { defineStore } from "pinia";

export const useAppStateStore = defineStore('appState', {
    state: () => ({
        loading: false,
        error:undefined,
        analysisModal: {
            promptsOptions: promptsData.prompts,
            selectedPromptId: promptsData.prompts[0].id,
            columnsCount: 3,
            prompt: promptsData.prompts[0].prompt,
            criteria: criteriaData.criteria.map((crit: string) => ({
                text: crit,
                selected: true
            }))
        }}),
        
    actions: {
        updatePrompt() {
            const selected = this.analysisModal.promptsOptions.find((p: { id: number }) => p.id === this.analysisModal.selectedPromptId);
            if (selected) {
                this.analysisModal.prompt = selected.prompt;
            }
        },
        getSelectedCriteria() {
            return this.analysisModal.criteria.filter((c: { selected: boolean }) => c.selected).map((c: { text: string }) => c.text);
        },
        getPrompt():string {
            const selected = this.analysisModal.promptsOptions.find((p: { id: number }) => p.id === this.analysisModal.selectedPromptId);
            if (selected) {
                return selected.prompt;
            }
            throw new Error("Prompt not found");
        }
    }
    
});