import { defineConfig, devices } from '@playwright/test'

const E2E_API_PORT = 8001
const E2E_WEB_PORT = 5174
const isCI = Boolean(process.env.CI)

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  reporter: isCI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: `http://localhost:${E2E_WEB_PORT}`,
    trace: 'retain-on-failure',
    locale: 'pt-BR',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] }, testMatch: /catalog\.spec\.ts/ },
  ],
  webServer: [
    {
      command: `sh -c "rm -f e2e.db && uv run alembic upgrade head && uv run python -m app.cli seed && uv run uvicorn app.main:app --port ${E2E_API_PORT}"`,
      cwd: '../backend',
      url: `http://localhost:${E2E_API_PORT}/health`,
      timeout: 180_000,
      reuseExistingServer: false,
      env: {
        ENVIRONMENT: 'test',
        DATABASE_URL: 'sqlite+aiosqlite:///./e2e.db',
        ADMIN_EMAIL: 'admin@rocketlab.dev',
        ADMIN_PASSWORD: 'rocketlab2026',
      },
    },
    {
      command: `npm run dev -- --port ${E2E_WEB_PORT} --strictPort`,
      url: `http://localhost:${E2E_WEB_PORT}`,
      reuseExistingServer: false,
      env: { API_PROXY_TARGET: `http://localhost:${E2E_API_PORT}` },
    },
  ],
})
