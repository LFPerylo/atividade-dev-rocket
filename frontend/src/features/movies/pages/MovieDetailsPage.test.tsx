import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import type { ReviewInput } from '@/domain/movie'
import { MovieDetailsPage } from '@/features/movies/pages/MovieDetailsPage'
import { API } from '@/test/handlers'
import { currentLocation, renderWithProviders } from '@/test/render'
import { server } from '@/test/server'

const renderDetails = (
  options: { authenticated?: boolean; route?: string; as?: 'admin' | 'avaliador' } = {},
) =>
  renderWithProviders(<MovieDetailsPage />, {
    route: options.route ?? '/filmes/m-cdd',
    path: '/filmes/:id',
    authenticated: options.authenticated,
    as: options.as,
  })

describe('MovieDetailsPage', () => {
  it('shows complete movie information', async () => {
    renderDetails()

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Cidade de Deus' }),
    ).toBeInTheDocument()
    expect(screen.getByText('2h 10min')).toBeInTheDocument()
    expect(screen.getByText('Fernando Meirelles, Kátia Lund')).toBeInTheDocument()
    expect(screen.getByText('Buscapé cresce em meio à violência.')).toBeInTheDocument()
    expect(screen.getByText('Alexandre Rodrigues')).toBeInTheDocument()
    expect(screen.getByText('O2 Filmes')).toBeInTheDocument()
    expect(screen.getByText('Crime')).toBeInTheDocument()
  })

  it('shows the average rating summary', async () => {
    renderDetails()

    const summary = await screen.findByRole('region', { name: 'Média das avaliações' })
    expect(within(summary).getByText('4,5')).toBeInTheDocument()
    expect(within(summary).getByText('2 avaliações')).toBeInTheDocument()
  })

  it('lists reviews', async () => {
    renderDetails()

    const list = await screen.findByRole('list', { name: 'Avaliações' })
    const items = within(list).getAllByRole('listitem')
    expect(items).toHaveLength(2)
    expect(within(items[0]!).getByText('Ana')).toBeInTheDocument()
    expect(within(items[0]!).getByText('Obra-prima.')).toBeInTheDocument()
    expect(within(items[0]!).getByRole('img', { name: 'Nota 5,0 de 5' })).toBeInTheDocument()
  })

  it('shows not found state for unknown movies', async () => {
    renderDetails({ route: '/filmes/inexistente' })

    expect(await screen.findByText('Filme não encontrado')).toBeInTheDocument()
  })

  it('invites visitors to sign in or create an account before reviewing', async () => {
    renderDetails()

    expect(await screen.findByRole('link', { name: 'Entre' })).toHaveAttribute(
      'href',
      '/login?next=%2Ffilmes%2Fm-cdd',
    )
    expect(screen.getByRole('link', { name: 'crie uma conta' })).toHaveAttribute(
      'href',
      '/cadastro?next=%2Ffilmes%2Fm-cdd',
    )
    expect(screen.queryByRole('button', { name: 'Publicar avaliação' })).not.toBeInTheDocument()
  })

  it('lets reviewers publish a review under their account', async () => {
    let payload: ReviewInput | null = null
    server.use(
      http.post(`${API}/movies/m-cdd/reviews`, async ({ request }) => {
        payload = (await request.json()) as ReviewInput
        return HttpResponse.json(
          { id: 'r9', nome: 'Bia Lima', ...payload, nota: 9, criado_em: '2026-09-24T12:00:00Z' },
          { status: 201 },
        )
      }),
    )
    renderDetails({ authenticated: true, as: 'avaliador' })

    expect(await screen.findByText('Avaliando como Bia Lima')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('radio', { name: '4,5 estrelas' }))
    await userEvent.type(screen.getByLabelText('Resenha'), 'Montagem impecável.')
    await userEvent.click(screen.getByRole('button', { name: 'Publicar avaliação' }))

    expect(await screen.findByText('Avaliação publicada')).toBeInTheDocument()
    expect(payload).toEqual({ estrelas: 4.5, comentario: 'Montagem impecável.' })
    await waitFor(() => expect(screen.getByLabelText('Resenha')).toHaveValue(''))
  })

  it('requires stars before publishing a review', async () => {
    renderDetails({ authenticated: true, as: 'avaliador' })

    await userEvent.type(await screen.findByLabelText('Resenha'), 'Bom.')
    await userEvent.click(screen.getByRole('button', { name: 'Publicar avaliação' }))

    expect(await screen.findByText('Escolha de 1 a 5 estrelas')).toBeInTheDocument()
  })

  it('hides movie management from reviewers', async () => {
    renderDetails({ authenticated: true, as: 'avaliador' })

    await screen.findByText('Avaliando como Bia Lima')
    expect(screen.queryByRole('link', { name: 'Editar' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Remover' })).not.toBeInTheDocument()
  })

  it('lets admins edit the movie', async () => {
    renderDetails({ authenticated: true })

    expect(await screen.findByRole('link', { name: 'Editar' })).toHaveAttribute(
      'href',
      '/filmes/m-cdd/editar',
    )
  })

  it('lets admins delete the movie after confirmation', async () => {
    const { container } = renderDetails({ authenticated: true })

    await userEvent.click(await screen.findByRole('button', { name: 'Remover' }))
    const dialog = screen.getByRole('dialog', { name: 'Remover “Cidade de Deus”?' })
    await userEvent.click(within(dialog).getByRole('button', { name: 'Remover filme' }))

    await waitFor(() => expect(currentLocation(container)).toBe('/'))
    expect(screen.getByText('Filme removido')).toBeInTheDocument()
  })
})
