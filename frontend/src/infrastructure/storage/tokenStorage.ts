const TOKEN_KEY = 'claquete.token'

export const tokenStorage = {
  read(): string | null {
    try {
      return window.localStorage.getItem(TOKEN_KEY)
    } catch {
      return null
    }
  },
  save(token: string): void {
    try {
      window.localStorage.setItem(TOKEN_KEY, token)
    } catch {
      return
    }
  },
  clear(): void {
    try {
      window.localStorage.removeItem(TOKEN_KEY)
    } catch {
      return
    }
  },
}
