import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { RegisterPage } from '@/features/auth/RegisterPage'
import { tokenStorage } from '@/infrastructure/storage/tokenStorage'
import { REVIEWER_TOKEN } from '@/test/handlers'
import { currentLocation, renderWithProviders } from '@/test/render'

const renderRegister = (route = '/cadastro') =>
  renderWithProviders(<RegisterPage />, { route, path: '/cadastro' })

async function fillForm(values: { nome: string; email: string; senha: string; confirmar: string }) {
  await userEvent.type(screen.getByLabelText('Nome'), values.nome)
  await userEvent.type(screen.getByLabelText('E-mail'), values.email)
  await userEvent.type(screen.getByLabelText('Senha'), values.senha)
  await userEvent.type(screen.getByLabelText('Confirme a senha'), values.confirmar)
  await userEvent.click(screen.getByRole('button', { name: 'Criar conta' }))
}

describe('RegisterPage', () => {
  it('creates the account, signs in and returns to the requested page', async () => {
    const { container } = renderRegister('/cadastro?next=/filmes/m-cdd')

    await fillForm({
      nome: 'Bia Lima',
      email: 'bia@exemplo.com',
      senha: 'senha-da-bia',
      confirmar: 'senha-da-bia',
    })

    await waitFor(() => expect(currentLocation(container)).toBe('/filmes/m-cdd'))
    expect(tokenStorage.read()).toBe(REVIEWER_TOKEN)
  })

  it('validates every field before calling the api', async () => {
    renderRegister()

    await fillForm({ nome: ' ', email: 'bia', senha: 'curta', confirmar: 'outra' })

    expect(await screen.findByText('Informe seu nome')).toBeInTheDocument()
    expect(screen.getByText('Informe um e-mail válido')).toBeInTheDocument()
    expect(screen.getByText('Use ao menos 8 caracteres')).toBeInTheDocument()
    expect(screen.getByText('As senhas não conferem')).toBeInTheDocument()
    expect(tokenStorage.read()).toBeNull()
  })

  it('shows when the e-mail is already registered', async () => {
    renderRegister()

    await fillForm({
      nome: 'Outra Pessoa',
      email: 'admin@rocketlab.dev',
      senha: 'senha-segura',
      confirmar: 'senha-segura',
    })

    expect(await screen.findByText('Já existe uma conta com este e-mail')).toBeInTheDocument()
  })

  it('links to login keeping the destination', () => {
    renderRegister('/cadastro?next=/filmes/m-cdd')

    expect(screen.getByRole('link', { name: 'Entrar' })).toHaveAttribute(
      'href',
      '/login?next=%2Ffilmes%2Fm-cdd',
    )
  })
})
