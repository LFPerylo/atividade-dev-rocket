import { http, HttpResponse } from 'msw'

import type { MovieDetails, MovieInput, ReviewInput } from '@/domain/movie'
import { cidadeDeDeus, ensaio, genres, pageOf, reviews } from '@/test/fixtures'

export const API = '*/api/v1'
export const VALID_TOKEN = 'token-valido'

const movies: Record<string, MovieDetails> = {
  [cidadeDeDeus.id]: cidadeDeDeus,
  [ensaio.id]: ensaio,
}

const isAuthorized = (request: Request) =>
  request.headers.get('authorization') === `Bearer ${VALID_TOKEN}`

const unauthorized = () =>
  HttpResponse.json({ detail: 'Sessão inválida ou expirada' }, { status: 401 })

export const handlers = [
  http.post(`${API}/auth/login`, async ({ request }) => {
    const { email, senha } = (await request.json()) as { email: string; senha: string }
    if (email === 'admin@rocketlab.dev' && senha === 'rocketlab2026') {
      return HttpResponse.json({
        access_token: VALID_TOKEN,
        token_type: 'bearer',
        expires_in: 3600,
      })
    }
    return HttpResponse.json({ detail: 'E-mail ou senha inválidos' }, { status: 401 })
  }),
  http.get(`${API}/auth/me`, ({ request }) =>
    isAuthorized(request)
      ? HttpResponse.json({ id: 'a1', email: 'admin@rocketlab.dev', nome: 'Administrador' })
      : unauthorized(),
  ),
  http.get(`${API}/genres`, () => HttpResponse.json(genres)),
  http.get(`${API}/movies`, ({ request }) => {
    const search = new URL(request.url).searchParams.get('busca')?.toLowerCase() ?? ''
    const found = Object.values(movies).filter((movie) =>
      movie.titulo.toLowerCase().includes(search),
    )
    return HttpResponse.json(pageOf(found))
  }),
  http.get(`${API}/movies/:id`, ({ params }) => {
    const movie = movies[String(params.id)]
    return movie
      ? HttpResponse.json(movie)
      : HttpResponse.json({ detail: `Filme ${String(params.id)} não encontrado` }, { status: 404 })
  }),
  http.post(`${API}/movies`, async ({ request }) => {
    if (!isAuthorized(request)) return unauthorized()
    const input = (await request.json()) as MovieInput
    return HttpResponse.json({ ...ensaio, ...input, id: 'm-new', generos: [] }, { status: 201 })
  }),
  http.put(`${API}/movies/:id`, async ({ request, params }) => {
    if (!isAuthorized(request)) return unauthorized()
    const input = (await request.json()) as MovieInput
    return HttpResponse.json({ ...movies[String(params.id)], ...input, generos: [] })
  }),
  http.delete(`${API}/movies/:id`, ({ request }) =>
    isAuthorized(request) ? new HttpResponse(null, { status: 204 }) : unauthorized(),
  ),
  http.get(`${API}/movies/:id/reviews`, () => HttpResponse.json(pageOf(reviews, 1, 5))),
  http.post(`${API}/movies/:id/reviews`, async ({ request }) => {
    if (!isAuthorized(request)) return unauthorized()
    const input = (await request.json()) as ReviewInput
    return HttpResponse.json(
      { id: 'r-new', ...input, nota: input.estrelas * 2, criado_em: '2026-09-24T12:00:00Z' },
      { status: 201 },
    )
  }),
]
