export const SORT_FIELDS = ['popularidade', 'media', 'titulo', 'ano'] as const
export const SORT_ORDERS = ['desc', 'asc'] as const

export type SortField = (typeof SORT_FIELDS)[number]
export type SortOrder = (typeof SORT_ORDERS)[number]

export type CatalogFilters = {
  busca: string
  genero: string
  anoDe: number | null
  anoAte: number | null
  estrelasMin: number | null
  ordenar: SortField
  ordem: SortOrder
  pagina: number
}

export const DEFAULT_FILTERS: CatalogFilters = {
  busca: '',
  genero: '',
  anoDe: null,
  anoAte: null,
  estrelasMin: null,
  ordenar: 'popularidade',
  ordem: 'desc',
  pagina: 1,
}

const PARAM_NAMES = {
  busca: 'busca',
  genero: 'genero',
  anoDe: 'ano_de',
  anoAte: 'ano_ate',
  estrelasMin: 'estrelas_min',
  ordenar: 'ordenar',
  ordem: 'ordem',
  pagina: 'pagina',
} as const satisfies Record<keyof CatalogFilters, string>

function parseNumber(value: string | null): number | null {
  if (value === null || value.trim() === '') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function parseOption<T extends string>(
  value: string | null,
  options: readonly T[],
  fallback: T,
): T {
  return options.find((option) => option === value) ?? fallback
}

export function filtersFromParams(params: URLSearchParams): CatalogFilters {
  const page = parseNumber(params.get(PARAM_NAMES.pagina))
  return {
    busca: params.get(PARAM_NAMES.busca) ?? DEFAULT_FILTERS.busca,
    genero: params.get(PARAM_NAMES.genero) ?? DEFAULT_FILTERS.genero,
    anoDe: parseNumber(params.get(PARAM_NAMES.anoDe)),
    anoAte: parseNumber(params.get(PARAM_NAMES.anoAte)),
    estrelasMin: parseNumber(params.get(PARAM_NAMES.estrelasMin)),
    ordenar: parseOption(params.get(PARAM_NAMES.ordenar), SORT_FIELDS, DEFAULT_FILTERS.ordenar),
    ordem: parseOption(params.get(PARAM_NAMES.ordem), SORT_ORDERS, DEFAULT_FILTERS.ordem),
    pagina: page !== null && Number.isInteger(page) && page >= 1 ? page : DEFAULT_FILTERS.pagina,
  }
}

export function filtersToParams(filters: CatalogFilters): URLSearchParams {
  const params = new URLSearchParams()
  for (const key of Object.keys(PARAM_NAMES) as (keyof CatalogFilters)[]) {
    const value = filters[key]
    if (value !== null && value !== DEFAULT_FILTERS[key]) {
      params.set(PARAM_NAMES[key], String(value))
    }
  }
  return params
}
