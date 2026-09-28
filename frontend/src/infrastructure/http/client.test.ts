import { http, HttpResponse } from 'msw'

import { ApiError, createHttpClient } from '@/infrastructure/http/client'
import { server } from '@/test/server'

const API = '*/api/v1'

function makeClient(token: string | null = null, onUnauthorized = vi.fn()) {
  return createHttpClient({ baseUrl: '/api/v1', getToken: () => token, onUnauthorized })
}

describe('http client', () => {
  it('sends query params skipping empty values', async () => {
    let received = ''
    server.use(
      http.get(`${API}/movies`, ({ request }) => {
        received = new URL(request.url).search
        return HttpResponse.json({ ok: true })
      }),
    )

    await makeClient().get('/movies', {
      query: { busca: 'nolan', genero: '', ano_de: null, pagina: 2 },
    })

    expect(received).toBe('?busca=nolan&pagina=2')
  })

  it('sends json body with bearer token', async () => {
    let authorization: string | null = null
    let body: unknown = null
    server.use(
      http.post(`${API}/movies`, async ({ request }) => {
        authorization = request.headers.get('authorization')
        body = await request.json()
        return HttpResponse.json({ id: 'm1' }, { status: 201 })
      }),
    )

    const result = await makeClient('abc').post<{ id: string }>('/movies', { titulo: 'X' })

    expect(result).toEqual({ id: 'm1' })
    expect(authorization).toBe('Bearer abc')
    expect(body).toEqual({ titulo: 'X' })
  })

  it('returns undefined for empty responses', async () => {
    server.use(http.delete(`${API}/movies/m1`, () => new HttpResponse(null, { status: 204 })))

    await expect(makeClient('abc').delete('/movies/m1')).resolves.toBeUndefined()
  })

  it('raises ApiError with backend detail message', async () => {
    server.use(
      http.get(`${API}/movies/x`, () =>
        HttpResponse.json({ detail: 'Filme x não encontrado' }, { status: 404 }),
      ),
    )

    await expect(makeClient().get('/movies/x')).rejects.toEqual(
      new ApiError(404, 'Filme x não encontrado'),
    )
  })

  it('uses first validation message for 422 responses', async () => {
    server.use(
      http.post(`${API}/movies`, () =>
        HttpResponse.json({ detail: [{ msg: 'Campo obrigatório' }] }, { status: 422 }),
      ),
    )

    await expect(makeClient().post('/movies', {})).rejects.toMatchObject({
      status: 422,
      message: 'Campo obrigatório',
    })
  })

  it('notifies unauthorized responses', async () => {
    const onUnauthorized = vi.fn()
    server.use(
      http.get(`${API}/auth/me`, () => HttpResponse.json({ detail: 'x' }, { status: 401 })),
    )

    await expect(makeClient('expired', onUnauthorized).get('/auth/me')).rejects.toBeInstanceOf(
      ApiError,
    )
    expect(onUnauthorized).toHaveBeenCalledOnce()
  })

  it('reports network failures', async () => {
    server.use(http.get(`${API}/genres`, () => HttpResponse.error()))

    await expect(makeClient().get('/genres')).rejects.toMatchObject({
      status: 0,
      message: 'Não foi possível conectar ao servidor',
    })
  })
})
