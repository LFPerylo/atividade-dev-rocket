import { Link } from 'react-router-dom'

import { useAuth } from '@/features/auth/authContext'
import { useMovies } from '@/features/movies/api'
import { FiltersPanel } from '@/features/movies/components/FiltersPanel'
import { MovieGrid, MovieGridSkeleton } from '@/features/movies/components/MovieGrid'
import { SearchBar } from '@/features/movies/components/SearchBar'
import { useCatalogFilters } from '@/features/movies/useCatalogFilters'
import { buttonClasses } from '@/shared/ui/buttonStyles'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Pagination } from '@/shared/ui/Pagination'

const countFormatter = new Intl.NumberFormat('pt-BR')

export function CatalogPage() {
  const { status } = useAuth()
  const { filters, update } = useCatalogFilters()
  const { data, isPending, isError, isPlaceholderData } = useMovies(filters)

  return (
    <section className="flex flex-col gap-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl font-semibold text-ink-100">Catálogo</h1>
          <p className="mt-1 text-sm text-ink-400">
            {data ? `${countFormatter.format(data.total)} filmes` : 'Carregando…'}
          </p>
        </div>
        {status === 'authenticated' && (
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
        <FiltersPanel filters={filters} onChange={update} />
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
