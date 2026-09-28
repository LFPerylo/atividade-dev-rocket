import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import { CatalogPage } from '@/features/movies/pages/CatalogPage'
import { pageOf } from '@/test/fixtures'
import { API } from '@/test/handlers'
import { currentLocation, renderWithProviders } from '@/test/render'
import { server } from '@/test/server'

describe('CatalogPage', () => {
  it('lists movies with average rating and link to details', async () => {
    renderWithProviders(<CatalogPage />)

    const card = await screen.findByRole('link', { name: /Cidade de Deus/ })
    expect(card).toHaveAttribute('href', '/filmes/m-cdd')
    expect(within(card).getByText('2002')).toBeInTheDocument()
    expect(within(card).getByRole('img', { name: 'Nota 4,5 de 5' })).toBeInTheDocument()
    expect(screen.getByText('2 filmes')).toBeInTheDocument()
  })

  it('searches by term and reflects it in the url', async () => {
    const { container } = renderWithProviders(<CatalogPage />)
    await screen.findByRole('link', { name: /Cidade de Deus/ })

    await userEvent.type(screen.getByRole('searchbox', { name: 'Buscar filmes' }), 'cegueira')

    await waitFor(() => expect(currentLocation(container)).toBe('/?busca=cegueira'))
    await waitFor(() =>
      expect(screen.queryByRole('link', { name: /Cidade de Deus/ })).not.toBeInTheDocument(),
    )
    expect(screen.getByRole('link', { name: /Ensaio sobre a Cegueira/ })).toBeInTheDocument()
  })

  it('reads initial filters from the url', async () => {
    renderWithProviders(<CatalogPage />, { route: '/?busca=cidade' })

    expect(await screen.findByRole('searchbox', { name: 'Buscar filmes' })).toHaveValue('cidade')
    expect(await screen.findByRole('link', { name: /Cidade de Deus/ })).toBeInTheDocument()
  })

  it('applies genre filter and resets pagination', async () => {
    const { container } = renderWithProviders(<CatalogPage />, { route: '/?pagina=2' })
    await screen.findByRole('option', { name: 'Crime' })

    await userEvent.selectOptions(screen.getByLabelText('Gênero'), 'g-crime')

    expect(currentLocation(container)).toBe('/?genero=g-crime')
  })

  it('changes sorting', async () => {
    const { container } = renderWithProviders(<CatalogPage />)

    await userEvent.selectOptions(screen.getByLabelText('Ordenar por'), 'titulo')

    expect(currentLocation(container)).toBe('/?ordenar=titulo')
  })

  it('shows empty state when nothing matches', async () => {
    server.use(http.get(`${API}/movies`, () => HttpResponse.json(pageOf([]))))
    renderWithProviders(<CatalogPage />, { route: '/?busca=zzz' })

    expect(await screen.findByText('Nenhum filme encontrado')).toBeInTheDocument()
  })

  it('shows error state when the api fails', async () => {
    server.use(
      http.get(`${API}/movies`, () => HttpResponse.json({ detail: 'Falhou' }, { status: 500 })),
    )
    renderWithProviders(<CatalogPage />)

    expect(await screen.findByText('Não foi possível carregar o catálogo')).toBeInTheDocument()
  })

  it('navigates between pages', async () => {
    server.use(
      http.get(`${API}/movies`, () =>
        HttpResponse.json({ ...pageOf([]), total: 50, pagina: 1, tamanho: 24, paginas: 3 }),
      ),
    )
    const { container } = renderWithProviders(<CatalogPage />)

    await userEvent.click(await screen.findByRole('button', { name: 'Próxima página' }))

    expect(currentLocation(container)).toBe('/?pagina=2')
  })

  it('offers movie creation only to admins', async () => {
    renderWithProviders(<CatalogPage />, { authenticated: true })
    expect(await screen.findByRole('link', { name: 'Adicionar filme' })).toHaveAttribute(
      'href',
      '/filmes/novo',
    )
  })

  it('hides movie creation from visitors', async () => {
    renderWithProviders(<CatalogPage />)
    await screen.findByRole('link', { name: /Cidade de Deus/ })

    expect(screen.queryByRole('link', { name: 'Adicionar filme' })).not.toBeInTheDocument()
  })
})
