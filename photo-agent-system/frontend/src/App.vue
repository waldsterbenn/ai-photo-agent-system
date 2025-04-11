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
                    <!-- Embedded component -->
                    <!-- <div class="d-flex align-items-center">

                    </div> -->
                </div>
            </div>
        </nav>
        <router-view></router-view>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';


export default defineComponent({
    name: 'App',
    components: {}
})
</script>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    text-align: center;
    margin-top: 1rem;
}
</style>