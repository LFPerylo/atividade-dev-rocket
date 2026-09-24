import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import type { MovieInput } from '@/domain/movie'
import { MovieCreatePage } from '@/features/movies/pages/MovieCreatePage'
import { MovieEditPage } from '@/features/movies/pages/MovieEditPage'
import { cidadeDeDeus } from '@/test/fixtures'
import { API } from '@/test/handlers'
import { currentLocation, renderWithProviders } from '@/test/render'
import { server } from '@/test/server'

function captureRequest(method: 'post' | 'put', path: string) {
  const captured: { body: MovieInput | null } = { body: null }
  server.use(
    http[method](`${API}${path}`, async ({ request }) => {
      captured.body = (await request.json()) as MovieInput
      return HttpResponse.json({ ...cidadeDeDeus, ...captured.body, id: 'm-new' }, { status: 201 })
    }),
  )
  return captured
}

describe('MovieCreatePage', () => {
  const renderCreate = () =>
    renderWithProviders(<MovieCreatePage />, {
      route: '/filmes/novo',
      path: '/filmes/novo',
      authenticated: true,
    })

  it('creates a movie and opens its page', async () => {
    const captured = captureRequest('post', '/movies')
    const { container } = renderCreate()

    await userEvent.type(await screen.findByLabelText('Título'), 'Central do Brasil')
    await userEvent.type(screen.getByLabelText('Diretores'), 'Walter Salles')
    await userEvent.click(await screen.findByRole('checkbox', { name: 'Drama' }))
    await userEvent.type(screen.getByLabelText('Ano de lançamento'), '1998')
    await userEvent.type(screen.getByLabelText('Sinopse'), 'Dora escreve cartas.')
    await userEvent.click(screen.getByRole('button', { name: 'Cadastrar filme' }))

    await waitFor(() => expect(currentLocation(container)).toBe('/filmes/m-new'))
    expect(screen.getByText('Filme cadastrado')).toBeInTheDocument()
    expect(captured.body).toMatchObject({
      titulo: 'Central do Brasil',
      diretores: ['Walter Salles'],
      generos: ['g-drama'],
      ano_lancamento: 1998,
      sinopse: 'Dora escreve cartas.',
    })
  })

  it('shows validation errors without calling the api', async () => {
    const captured = captureRequest('post', '/movies')
    renderCreate()

    await userEvent.click(await screen.findByRole('button', { name: 'Cadastrar filme' }))

    expect(await screen.findByText('Informe o título')).toBeInTheDocument()
    expect(captured.body).toBeNull()
  })

  it('shows api errors', async () => {
    server.use(
      http.post(`${API}/movies`, () =>
        HttpResponse.json({ detail: 'Gêneros inexistentes: g-x' }, { status: 422 }),
      ),
    )
    renderCreate()

    await userEvent.type(await screen.findByLabelText('Título'), 'X')
    await userEvent.click(screen.getByRole('button', { name: 'Cadastrar filme' }))

    expect(await screen.findByText('Gêneros inexistentes: g-x')).toBeInTheDocument()
  })
})

describe('MovieEditPage', () => {
  it('prefills and updates the movie', async () => {
    const captured = captureRequest('put', '/movies/m-cdd')
    const { container } = renderWithProviders(<MovieEditPage />, {
      route: '/filmes/m-cdd/editar',
      path: '/filmes/:id/editar',
      authenticated: true,
    })

    const title = await screen.findByLabelText('Título')
    expect(title).toHaveValue('Cidade de Deus')
    expect(await screen.findByRole('checkbox', { name: 'Crime' })).toBeChecked()

    await userEvent.clear(title)
    await userEvent.type(title, 'City of God')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(currentLocation(container)).toBe('/filmes/m-cdd'))
    expect(screen.getByText('Filme atualizado')).toBeInTheDocument()
    expect(captured.body).toMatchObject({ titulo: 'City of God', generos: ['g-crime', 'g-drama'] })
  })
})
