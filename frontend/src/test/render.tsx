import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'

import { AuthProvider } from '@/features/auth/AuthProvider'
import { tokenStorage } from '@/infrastructure/storage/tokenStorage'
import { ToastProvider } from '@/shared/ui/Toast'
import { VALID_TOKEN } from '@/test/handlers'

type RenderOptions = {
  route?: string
  path?: string
  authenticated?: boolean
}

function LocationProbe() {
  const location = useLocation()
  return <output data-testid="location">{`${location.pathname}${location.search}`}</output>
}

export function renderWithProviders(
  element: ReactElement,
  { route = '/', path = '/', authenticated = false }: RenderOptions = {},
) {
  if (authenticated) tokenStorage.save(VALID_TOKEN)
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <MemoryRouter initialEntries={[route]}>
          <AuthProvider>
            <Routes>
              <Route path={path} element={element} />
              <Route path="*" element={<p>Outra página</p>} />
            </Routes>
            <LocationProbe />
          </AuthProvider>
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>,
  )
}

export const currentLocation = (container: HTMLElement) =>
  container.querySelector('[data-testid="location"]')?.textContent
