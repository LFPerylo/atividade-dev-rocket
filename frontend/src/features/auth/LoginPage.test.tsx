import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { LoginPage } from '@/features/auth/LoginPage'
import { tokenStorage } from '@/infrastructure/storage/tokenStorage'
import { currentLocation, renderWithProviders } from '@/test/render'

async function fillAndSubmit(email: string, password: string) {
  await userEvent.type(screen.getByLabelText('E-mail'), email)
  await userEvent.type(screen.getByLabelText('Senha'), password)
  await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
}

describe('LoginPage', () => {
  it('logs in and redirects to requested page', async () => {
    const { container } = renderWithProviders(<LoginPage />, {
      route: '/login?next=/filmes/novo',
      path: '/login',
    })

    await fillAndSubmit('admin@rocketlab.dev', 'rocketlab2026')

    await waitFor(() => expect(currentLocation(container)).toBe('/filmes/novo'))
    expect(tokenStorage.read()).toBe('token-valido')
  })

  it('shows backend error for invalid credentials', async () => {
    renderWithProviders(<LoginPage />, { route: '/login', path: '/login' })

    await fillAndSubmit('admin@rocketlab.dev', 'senha-errada')

    expect(await screen.findByText('E-mail ou senha inválidos')).toBeInTheDocument()
    expect(tokenStorage.read()).toBeNull()
  })

  it('validates required fields', async () => {
    renderWithProviders(<LoginPage />, { route: '/login', path: '/login' })

    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Informe um e-mail válido')).toBeInTheDocument()
    expect(screen.getByText('Informe a senha')).toBeInTheDocument()
  })

  it('ignores external redirect targets', async () => {
    const { container } = renderWithProviders(<LoginPage />, {
      route: '/login?next=//malicioso.com',
      path: '/login',
    })

    await fillAndSubmit('admin@rocketlab.dev', 'rocketlab2026')

    await waitFor(() => expect(currentLocation(container)).toBe('/'))
  })
})
