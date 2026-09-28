import { screen, waitFor } from '@testing-library/react'

import { RequireAdmin } from '@/features/auth/RequireAdmin'
import { currentLocation, renderWithProviders } from '@/test/render'

const protectedPage = (
  <RequireAdmin>
    <p>Área restrita</p>
  </RequireAdmin>
)

describe('RequireAdmin', () => {
  it('renders children for admins', async () => {
    renderWithProviders(protectedPage, {
      route: '/filmes/novo',
      path: '/filmes/novo',
      authenticated: true,
    })

    expect(await screen.findByText('Área restrita')).toBeInTheDocument()
  })

  it('explains that reviewers cannot access admin pages', async () => {
    renderWithProviders(protectedPage, {
      route: '/filmes/novo',
      path: '/filmes/novo',
      authenticated: true,
      as: 'avaliador',
    })

    expect(await screen.findByText('Acesso restrito a administradores')).toBeInTheDocument()
    expect(screen.queryByText('Área restrita')).not.toBeInTheDocument()
  })

  it('redirects visitors to login keeping destination', async () => {
    const { container } = renderWithProviders(protectedPage, {
      route: '/filmes/novo',
      path: '/filmes/novo',
    })

    await waitFor(() => expect(currentLocation(container)).toBe('/login?next=%2Ffilmes%2Fnovo'))
  })
})
