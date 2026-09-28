import type { ReactNode } from 'react'

import { formatCompactNumber, formatDate, formatUsd } from '@/domain/format'
import type { MovieDetails } from '@/domain/movie'

const CAST_LIMIT = 12

function Fact({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <dt className="text-sm text-ink-400">{label}</dt>
      <dd className="text-sm font-medium text-ink-100">{children}</dd>
    </div>
  )
}

export function MovieFacts({ movie }: { movie: MovieDetails }) {
  const performance = movie.desempenho
  const budget = formatUsd(performance?.orcamento_usd ?? null)
  const revenue = formatUsd(performance?.receita_usd ?? null)
  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-5 sm:grid-cols-3">
      {movie.data_lancamento && <Fact label="Lançamento">{formatDate(movie.data_lancamento)}</Fact>}
      {movie.status && <Fact label="Status">{movie.status}</Fact>}
      {movie.roteiristas.length > 0 && <Fact label="Roteiro">{movie.roteiristas.join(', ')}</Fact>}
      {movie.produtoras.length > 0 && (
        <Fact label="Produção">
          <ul>
            {movie.produtoras.map((company) => (
              <li key={company}>{company}</li>
            ))}
          </ul>
        </Fact>
      )}
      {performance?.nota_imdb != null && (
        <Fact label="IMDb">
          {performance.nota_imdb.toFixed(1)}
          {performance.votos_imdb != null && (
            <span className="text-ink-500">
              {' '}
              · {formatCompactNumber(performance.votos_imdb)} votos
            </span>
          )}
        </Fact>
      )}
      {performance?.nota_tmdb != null && (
        <Fact label="TMDB">{performance.nota_tmdb.toFixed(1)}</Fact>
      )}
      {budget && <Fact label="Orçamento">{budget}</Fact>}
      {revenue && <Fact label="Bilheteria">{revenue}</Fact>}
      {movie.elenco.length > 0 && (
        <div className="col-span-full flex flex-col gap-2">
          <dt className="text-sm text-ink-400">Elenco</dt>
          <dd>
            <ul className="flex flex-wrap gap-2">
              {movie.elenco.slice(0, CAST_LIMIT).map((actor) => (
                <li key={actor} className="rounded-full bg-ink-800 px-3 py-1 text-xs text-ink-200">
                  {actor}
                </li>
              ))}
            </ul>
          </dd>
        </div>
      )}
    </dl>
  )
}
