import vue from "@vitejs/plugin-vue";
import vueJsx from '@vitejs/plugin-vue-jsx';
import path from "path";
import { defineConfig } from 'vite';
import vueDevTools from 'vite-plugin-vue-devtools';


export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Map '@' to the 'src' directory
    },
  },
  server: {
    host: "0.0.0.0",
    port: 8080,
    watch: {
      usePolling: true // Use polling to watch for file changes
    }
  }  
});
