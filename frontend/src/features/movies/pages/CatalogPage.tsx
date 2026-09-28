import { SlidersHorizontalIcon } from '@phosphor-icons/react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { DEFAULT_FILTERS } from '@/domain/filters'
import { useAuth } from '@/features/auth/authContext'
import { useMovies } from '@/features/movies/api'
import { FiltersPanel } from '@/features/movies/components/FiltersPanel'
import { MovieGrid, MovieGridSkeleton } from '@/features/movies/components/MovieGrid'
import { SearchBar } from '@/features/movies/components/SearchBar'
import { useCatalogFilters } from '@/features/movies/useCatalogFilters'
import { Button } from '@/shared/ui/Button'
import { buttonClasses } from '@/shared/ui/buttonStyles'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Pagination } from '@/shared/ui/Pagination'

const countFormatter = new Intl.NumberFormat('pt-BR')
const FILTER_KEYS = ['genero', 'anoDe', 'anoAte', 'estrelasMin'] as const

export function CatalogPage() {
  const { isAdmin } = useAuth()
  const { filters, update } = useCatalogFilters()
  const { data, isPending, isError, isPlaceholderData } = useMovies(filters)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const activeFilters = FILTER_KEYS.filter((key) => filters[key] !== DEFAULT_FILTERS[key]).length

  return (
    <section className="flex flex-col gap-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl font-semibold text-ink-100">Catálogo</h1>
          <p className="mt-1 text-sm text-ink-400">
            {data ? `${countFormatter.format(data.total)} filmes` : 'Carregando…'}
          </p>
        </div>
        {isAdmin && (
          <Link to="/filmes/novo" className={buttonClasses('primary')}>
            Adicionar filme
          </Link>
        )}
      </header>

      <div className="flex flex-col gap-4 rounded-xl border border-ink-800 bg-ink-950/40 p-4">
        <SearchBar
          initialValue={filters.busca}
          onSearch={(busca) => update({ busca }, { replace: true })}
        />
        <Button
          variant="ghost"
          className="self-start md:hidden"
          aria-expanded={filtersOpen}
          aria-controls="catalog-filters"
          onClick={() => setFiltersOpen((open) => !open)}
        >
          <SlidersHorizontalIcon aria-hidden="true" weight="bold" className="size-4" />
          Filtros{activeFilters > 0 && ` (${activeFilters})`}
        </Button>
        <div id="catalog-filters" className={filtersOpen ? 'block' : 'hidden md:block'}>
          <FiltersPanel filters={filters} onChange={update} />
        </div>
      </div>

      {isPending && <MovieGridSkeleton />}
      {isError && (
        <EmptyState
          title="Não foi possível carregar o catálogo"
          description="Verifique sua conexão e tente novamente."
        />
      )}
      {data && data.itens.length === 0 && (
        <EmptyState
          title="Nenhum filme encontrado"
          description="Tente outro termo de busca ou ajuste os filtros."
        />
      )}
      {data && data.itens.length > 0 && (
        <div className={isPlaceholderData ? 'opacity-60 transition-opacity' : undefined}>
          <MovieGrid movies={data.itens} />
        </div>
      )}
      {data && (
        <Pagination
          page={data.pagina}
          pages={data.paginas}
          onChange={(pagina) => {
            update({ pagina })
            window.scrollTo({ top: 0, behavior: 'smooth' })
          }}
        />
      )}
    </section>
  )
}
