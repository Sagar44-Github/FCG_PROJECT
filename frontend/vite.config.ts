import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    proxy: { '/api': { target: process.env.VITE_API_PROXY ?? 'http://127.0.0.1:8000', changeOrigin: true } },
  },
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'three-vendor', test: /node_modules[\\/](three|three-stdlib|@react-three[\\/]|camera-controls|meshline)[\\/]/, priority: 20, maxSize: 440_000 },
            { name: 'chart-vendor', test: /node_modules[\\/](recharts|d3-[^\\/]+|victory-vendor)[\\/]/, priority: 10 },
            { name: 'vendor', test: /node_modules[\\/]/, priority: 0, maxSize: 650_000 },
          ],
        },
      },
    },
  },
})
