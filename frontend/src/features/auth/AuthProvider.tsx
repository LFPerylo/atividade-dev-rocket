import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { authApi } from '@/features/auth/api'
import { AuthContext, type AuthStatus } from '@/features/auth/authContext'
import { UNAUTHORIZED_EVENT } from '@/infrastructure/http/apiClient'
import { tokenStorage } from '@/infrastructure/storage/tokenStorage'

const meKey = (token: string | null) => ['auth', 'me', token] as const

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [token, setToken] = useState<string | null>(tokenStorage.read)
  const me = useQuery({
    queryKey: meKey(token),
    queryFn: authApi.me,
    enabled: token !== null,
    retry: false,
    staleTime: Infinity,
  })

  const logout = useCallback(() => {
    tokenStorage.clear()
    setToken(null)
    queryClient.removeQueries({ queryKey: ['auth'] })
  }, [queryClient])

  const login = useCallback(
    async (email: string, senha: string) => {
      const { access_token: newToken } = await authApi.login(email, senha)
      tokenStorage.save(newToken)
      await queryClient.fetchQuery({ queryKey: meKey(newToken), queryFn: authApi.me })
      setToken(newToken)
    },
    [queryClient],
  )

  useEffect(() => {
    window.addEventListener(UNAUTHORIZED_EVENT, logout)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, logout)
  }, [logout])

  const status: AuthStatus =
    token === null || me.isError ? 'anonymous' : me.data ? 'authenticated' : 'loading'
  const admin = status === 'authenticated' ? (me.data ?? null) : null

  const value = useMemo(() => ({ status, admin, login, logout }), [status, admin, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
