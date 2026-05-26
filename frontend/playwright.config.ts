import { defineConfig, devices } from '@playwright/test'
import { fileURLToPath } from 'url'

// Absolute path to the Django backend (sibling of this frontend/ dir).
const backendDir = fileURLToPath(new URL('../backend', import.meta.url))

// Dedicated test ports so E2E doesn't collide with a manually-running
// dev stack (which may use other ports).
const BACKEND_PORT = 8000
const FRONTEND_PORT = 5174
const BASE_URL = `http://localhost:${FRONTEND_PORT}`

export default defineConfig({
  testDir: './e2e',
  // Each spec creates its own account; serial avoids cross-test interference
  // and keeps output readable. Bump workers once tests are fully isolated.
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [['html', { open: 'never' }], ['list']],
  timeout: 60_000,
  expect: { timeout: 10_000 },

  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],

  // Playwright boots both servers and waits for them to be reachable.
  webServer: [
    {
      // --noreload keeps the process tree simple so Playwright can stop it cleanly.
      command: `python manage.py runserver 127.0.0.1:${BACKEND_PORT} --noreload`,
      cwd: backendDir,
      url: `http://127.0.0.1:${BACKEND_PORT}/api/docs`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      // Point the Vite proxy at the test backend regardless of frontend/.env.
      command: `npm run dev -- --port ${FRONTEND_PORT} --strictPort`,
      url: BASE_URL,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: { VITE_API_TARGET: `http://127.0.0.1:${BACKEND_PORT}` },
    },
  ],
})
