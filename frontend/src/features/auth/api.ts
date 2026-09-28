import type { Admin } from '@/domain/movie'
import { apiClient } from '@/infrastructure/http/apiClient'

type TokenResponse = {
  access_token: string
  token_type: string
  expires_in: number
}

export const authApi = {
  login: (email: string, senha: string) =>
    apiClient.post<TokenResponse>('/auth/login', { email, senha }),
  me: () => apiClient.get<Admin>('/auth/me'),
}
