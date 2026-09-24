import { createHttpClient } from '@/infrastructure/http/client'
import { tokenStorage } from '@/infrastructure/storage/tokenStorage'

export const UNAUTHORIZED_EVENT = 'claquete:unauthorized'

export const apiClient = createHttpClient({
  baseUrl: import.meta.env.VITE_API_URL ?? '/api/v1',
  getToken: tokenStorage.read,
  onUnauthorized: () => window.dispatchEvent(new Event(UNAUTHORIZED_EVENT)),
})
