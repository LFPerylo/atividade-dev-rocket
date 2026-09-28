import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Layout } from '@/app/Layout'
import { tokenStorage } from '@/infrastructure/storage/tokenStorage'
import { renderWithProviders } from '@/test/render'

describe('Layout', () => {
  it('offers login and sign-up to visitors', () => {
    renderWithProviders(<Layout />)

    expect(screen.getByRole('link', { name: 'Entrar' })).toHaveAttribute('href', '/login')
    expect(screen.getByRole('link', { name: 'Criar conta' })).toHaveAttribute('href', '/cadastro')
    expect(screen.getByRole('link', { name: 'Claquete — início' })).toHaveAttribute('href', '/')
  })

  it('shows the admin and logs out', async () => {
    renderWithProviders(<Layout />, { authenticated: true })

    expect(await screen.findByText('Administrador')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Sair' }))

    expect(screen.getByRole('link', { name: 'Entrar' })).toBeInTheDocument()
    expect(tokenStorage.read()).toBeNull()
  })
})
