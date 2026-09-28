import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'

import { server } from '@/test/server'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
  window.localStorage.clear()
})
afterAll(() => server.close())
