import { DEFAULT_FILTERS, filtersFromParams, filtersToParams } from '@/domain/filters'

describe('catalog filters', () => {
  it('uses defaults when params are empty', () => {
    expect(filtersFromParams(new URLSearchParams())).toEqual(DEFAULT_FILTERS)
  })

  it('parses every supported param', () => {
    const params = new URLSearchParams(
      'busca=matrix&genero=g1&ano_de=1990&ano_ate=2000&estrelas_min=4&ordenar=titulo&ordem=asc&pagina=3',
    )

    expect(filtersFromParams(params)).toEqual({
      busca: 'matrix',
      genero: 'g1',
      anoDe: 1990,
      anoAte: 2000,
      estrelasMin: 4,
      ordenar: 'titulo',
      ordem: 'asc',
      pagina: 3,
    })
  })

  it('ignores invalid values', () => {
    const params = new URLSearchParams('ano_de=abc&ordenar=x&ordem=y&pagina=-2')

    expect(filtersFromParams(params)).toEqual(DEFAULT_FILTERS)
  })

  it('serializes only non-default values', () => {
    const params = filtersToParams({ ...DEFAULT_FILTERS, busca: 'nolan', pagina: 2 })

    expect(params.toString()).toBe('busca=nolan&pagina=2')
  })

  it('round-trips filters', () => {
    const filters = { ...DEFAULT_FILTERS, genero: 'g2', estrelasMin: 3.5, ordem: 'asc' as const }

    expect(filtersFromParams(filtersToParams(filters))).toEqual(filters)
  })
})
