<template>
    <div id="app" class="container">
        <nav class="navbar navbar-expand border mb-2">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">Photo album</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                        <li class="nav-item">
                            <router-link to="/" class="nav-link">Main</router-link>
                        </li>
                        <!-- <li class="nav-item">
                            <router-link to="/api" class="nav-link">A link</router-link>
                        </li> -->
                    </ul>
                    <div class="d-flex align-items-center">
                        <i v-if="backendAvailable" class="bi bi-check-circle-fill text-success"
                            title="Backend connected"></i>
                        <i v-else class="bi bi-x-circle-fill text-danger" title="Backend disconnected"></i>
                    </div>
                    <div class="d-flex align-items-center ms-3">
                        <i v-if="agentsAvailable" class="bi bi-check-circle-fill text-success"
                            title="Agent connected"></i>
                        <i v-else class="bi bi-x-circle-fill text-danger" title="Agent disconnected"></i>
                    </div>
                    <div class="d-flex align-items-center ms-3">
                        <i v-if="dbAvailable" class="bi bi-check-circle-fill text-success" title="DB connected"></i>
                        <i v-else class="bi bi-x-circle-fill text-danger" title="DB disconnected"></i>
                    </div>
                </div>
            </div>
        </nav>
        <router-view></router-view>
    </div>
</template>

<script lang="ts" setup>
import axios from 'axios';
import { computed, onMounted, ref } from 'vue';
import { backendUrl } from './config/backend_conf';

const backendAvailable = ref(false);
const agentsAvailable = ref(false);
const dbAvailable = ref(false);

const backendStatus = computed(() => `${backendUrl}/api`);
const agentStatus = computed(() => `${backendUrl}/agent-status`);
const dbStatus = computed(() => `${backendUrl}/db-status`);

onMounted(() => {
    axios.get(backendStatus.value)
        .then(response => {
            // Assume a successful response means the backend is available.
            backendAvailable.value = true;
            console.debug("Backend connected", response?.data ?? "No message");

        })
        .catch(error => {
            // On error, mark the backend as unavailable.
            backendAvailable.value = false;
            console.error("Backend connection failed:", error);
        });

    axios.get(agentStatus.value)
        .then(response => {
            // Assume a successful response means the backend is available.
            agentsAvailable.value = true;
            console.debug("Agents backend connected", response?.data ?? "No message");
        })
        .catch(error => {
            // On error, mark the backend as unavailable.
            agentsAvailable.value = false;
            console.error("Agents connection failed:", error);
        });

    axios.get(dbStatus.value)
        .then(response => {
            // Assume a successful response means the backend is available.
            dbAvailable.value = true;
            console.debug("DB backend connected", response?.data ?? "No message");
        })
        .catch(error => {
            // On error, mark the backend as unavailable.
            dbAvailable.value = false;
            console.error("DB connection failed:", error);
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