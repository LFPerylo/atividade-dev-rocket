import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'

import { type CatalogFilters, filtersFromParams, filtersToParams } from '@/domain/filters'

export function useCatalogFilters() {
  const [params, setParams] = useSearchParams()
  const filters = useMemo(() => filtersFromParams(params), [params])

  const update = useCallback(
    (changes: Partial<CatalogFilters>, options: { replace?: boolean } = {}) => {
      const resetsPage = !('pagina' in changes)
      const next = { ...filters, ...changes, ...(resetsPage ? { pagina: 1 } : {}) }
      setParams(filtersToParams(next), { replace: options.replace ?? false })
    },
    [filters, setParams],
  )

  return { filters, update }
}
