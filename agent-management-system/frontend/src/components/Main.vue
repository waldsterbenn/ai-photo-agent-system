<template>
    <div>
        <h1>Service Status</h1>
        <p>Calling URL: {{ statusUrl }}</p>
        <p v-if="loading">Loading...</p>
        <p v-else-if="error">{{ error }}</p>
        <p v-else>{{ status }}</p>
    </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { computed, onMounted, ref } from 'vue';
import { backendUrl } from '../config/backend_conf';

const statusUrl = computed(() => `${backendUrl}/status`);
const status = ref('');
const loading = ref(true);
const error = ref('');

const fetchStatus = async () => {
    try {
        const response = await axios.get(statusUrl.value);
        status.value = JSON.stringify(response.data);
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchStatus();
});
</script>

<style scoped>
h1 {
    font-size: 24px;
    margin-bottom: 20px;
}
</style>