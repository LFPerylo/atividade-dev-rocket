import { screen, waitFor } from '@testing-library/react'

import { RequireAuth } from '@/features/auth/RequireAuth'
import { currentLocation, renderWithProviders } from '@/test/render'

describe('RequireAuth', () => {
  it('renders children for authenticated admins', async () => {
    renderWithProviders(
      <RequireAuth>
        <p>Área restrita</p>
      </RequireAuth>,
      { route: '/filmes/novo', path: '/filmes/novo', authenticated: true },
    )

    expect(await screen.findByText('Área restrita')).toBeInTheDocument()
  })

  it('redirects anonymous visitors to login keeping destination', async () => {
    const { container } = renderWithProviders(
      <RequireAuth>
        <p>Área restrita</p>
      </RequireAuth>,
      { route: '/filmes/novo', path: '/filmes/novo' },
    )

    await waitFor(() => expect(currentLocation(container)).toBe('/login?next=%2Ffilmes%2Fnovo'))
    expect(screen.queryByText('Área restrita')).not.toBeInTheDocument()
  })
})
