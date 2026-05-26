import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load .env files. The backend URL is configurable via VITE_API_TARGET so
  // you can point the dev server at a backend running on any host/port.
  const env = loadEnv(mode, process.cwd(), '')
  // process.env wins (used by Playwright/CI to point at a test backend),
  // then .env files, then the default.
  const apiTarget = process.env.VITE_API_TARGET || env.VITE_API_TARGET || 'http://localhost:8000'

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
        '/ai': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
