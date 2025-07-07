import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      // This will proxy any request starting with /api to your backend
      '/api': {
        target: 'http://localhost:8085',
        // This is necessary for the backend to accept the request
        changeOrigin: true,
      },
    }
  }
})
