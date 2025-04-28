<template>
    <div id="app" class="container">
        <nav class="navbar navbar-expand border mb-2">
            <div class="container-fluid">
                <!-- <a class="navbar-brand" href="#">Photo album</a> -->
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                        <!-- <li class="nav-item">
                            <router-link to="/" class="nav-link">Main</router-link>
                        </li> -->
                        <!-- <li class="nav-item">
                            <router-link to="/api" class="nav-link">A link</router-link>
                        </li> -->
                    </ul>
                    <div class="d-flex align-items-center ms-3">
                        <div v-if="backendAvailable === undefined" class="spinner-grow spinner-grow-sm" role="status"
                            title="Backend pending...">
                            <span class="visually-hidden">Backend pending...</span>
                        </div>
                        <i v-else-if="backendAvailable" class="bi bi-check-circle-fill text-success"
                            title="Backend connected"></i>
                        <i v-else class="bi bi-x-circle-fill text-danger" title="Backend disconnected"></i>
                    </div>
                    <div class="d-flex align-items-center ms-3">
                        <div v-if="agentsAvailable === undefined" class="spinner-grow spinner-grow-sm" role="status"
                            title="Agent pending...">
                            <span class="visually-hidden">Agent pending...</span>
                        </div>
                        <i v-else-if="agentsAvailable" class="bi bi-check-circle-fill text-success"
                            title="Agent connected"></i>
                        <i v-else class="bi bi-x-circle-fill text-danger" title="Agent disconnected"></i>
                    </div>
                    <div class="d-flex align-items-center ms-3">
                        <div v-if="dbAvailable === undefined" class="spinner-grow spinner-grow-sm" role="status"
                            title="DB pending...">
                            <span class="visually-hidden">DB pending...</span>
                        </div>
                        <i v-else-if="dbAvailable" class="bi bi-check-circle-fill text-success"
                            title="DB connected"></i>
                        <i v-else class="bi bi-x-circle-fill text-danger" title="DB disconnected"></i>
                    </div>
                </div>
            </div>
        </nav>
        <router-view></router-view>
    </div>
</template>

<script lang="ts" setup>
import { useAppStateStore } from '@/stores/appStateStore';
import axios from 'axios';
import { computed, onMounted, ref, watch } from 'vue';
import { backendUrl } from './config/backend_conf';
console.debug(`Backend URL: ${backendUrl}`);

const appStateStore = useAppStateStore();

const backendAvailable = ref();
const agentsAvailable = ref();
const dbAvailable = ref();

watch([backendAvailable, agentsAvailable, dbAvailable], () => {
    appStateStore.allSystemsNominal = backendAvailable.value && agentsAvailable.value && dbAvailable.value;
});

const backendStatusUrl = computed(() => `${backendUrl}/api`);
const agentStatusUrl = computed(() => `${backendUrl}/agent-status`);
const dbStatusUrl = computed(() => `${backendUrl}/db-status`);

onMounted(() => {
    axios.get(backendStatusUrl.value)
        .then(response => {
            // Assume a successful response means the backend is available.
            backendAvailable.value = true;
            console.debug(`Backend connected (${backendStatusUrl})`, response?.data ?? "No message");
        })
        .catch(error => {
            // On error, mark the backend as unavailable.
            backendAvailable.value = false;
            console.error(`Backend failed (${backendStatusUrl})`, error);
            appStateStore.error = error.message || JSON.stringify(error);
        });

    axios.get(agentStatusUrl.value)
        .then(response => {
            // Assume a successful response means the backend is available.
            agentsAvailable.value = true;
            console.debug(`Agent connected (${agentStatusUrl})`, response?.data ?? "No message");
        })
        .catch(error => {
            // On error, mark the backend as unavailable.
            agentsAvailable.value = false;
            console.error(`Agent failed (${agentStatusUrl})`, error);
            appStateStore.error = error.message || JSON.stringify(error);
        });

    axios.get(dbStatusUrl.value)
        .then(response => {
            // Assume a successful response means the backend is available.
            dbAvailable.value = true;
            console.debug(`DB connected (${dbStatusUrl})`, response?.data ?? "No message");
        })
        .catch(error => {
            // On error, mark the backend as unavailable.
            dbAvailable.value = false;
            console.error(`DB failed (${dbStatusUrl})`, error);
            appStateStore.error = error.message || JSON.stringify(error);
        });
});

</script>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    text-align: center;
    margin-top: 1rem;
}
</style>