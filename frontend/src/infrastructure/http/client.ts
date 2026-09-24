export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type QueryValue = string | number | null | undefined

type RequestOptions = {
  query?: Record<string, QueryValue>
  body?: unknown
  signal?: AbortSignal
}

type ClientConfig = {
  baseUrl: string
  getToken: () => string | null
  onUnauthorized: () => void
}

export type HttpClient = {
  get<T>(path: string, options?: Omit<RequestOptions, 'body'>): Promise<T>
  post<T>(path: string, body?: unknown): Promise<T>
  put<T>(path: string, body?: unknown): Promise<T>
  delete(path: string): Promise<void>
}

const NETWORK_ERROR_MESSAGE = 'Não foi possível conectar ao servidor'
const UNAUTHORIZED = 401
const NO_CONTENT = 204

type ErrorBody = { detail?: string | { msg?: string }[] }

function buildUrl(baseUrl: string, path: string, query: RequestOptions['query']): string {
  const url = new URL(`${baseUrl}${path}`, window.location.origin)
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== null && value !== undefined && value !== '') {
      url.searchParams.set(key, String(value))
    }
  }
  return url.toString()
}

async function errorMessage(response: Response): Promise<string> {
  const fallback = `Erro inesperado (${response.status})`
  try {
    const { detail } = (await response.json()) as ErrorBody
    if (typeof detail === 'string') return detail
    return detail?.[0]?.msg ?? fallback
  } catch {
    return fallback
  }
}

export function createHttpClient({ baseUrl, getToken, onUnauthorized }: ClientConfig): HttpClient {
  async function request<T>(
    method: string,
    path: string,
    options: RequestOptions = {},
  ): Promise<T> {
    const token = getToken()
    const headers: Record<string, string> = { Accept: 'application/json' }
    if (options.body !== undefined) headers['Content-Type'] = 'application/json'
    if (token) headers.Authorization = `Bearer ${token}`

    let response: Response
    try {
      response = await fetch(buildUrl(baseUrl, path, options.query), {
        method,
        headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
        signal: options.signal,
      })
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') throw error
      throw new ApiError(0, NETWORK_ERROR_MESSAGE)
    }

    if (response.status === UNAUTHORIZED) onUnauthorized()
    if (!response.ok) throw new ApiError(response.status, await errorMessage(response))
    if (response.status === NO_CONTENT) return undefined as T
    return (await response.json()) as T
  }

  return {
    get: (path, options) => request('GET', path, options),
    post: (path, body) => request('POST', path, { body }),
    put: (path, body) => request('PUT', path, { body }),
    delete: (path) => request('DELETE', path),
  }
}
