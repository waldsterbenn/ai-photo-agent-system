import vue from "@vitejs/plugin-vue";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue()],
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
