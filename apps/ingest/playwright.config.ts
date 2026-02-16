import { defineConfig, devices } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || process.env.TEST_BASE_URL || 'http://localhost:3007'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 2 : undefined,
  reporter: 'html',
  timeout: 15000,
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev:test',
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 90_000,
  },
})
