import { Link } from 'react-router-dom'

import type { MovieSummary } from '@/domain/movie'
import { MoviePoster } from '@/features/movies/components/MoviePoster'
import { StarRating } from '@/shared/ui/StarRating'

export function MovieCard({ movie }: { movie: MovieSummary }) {
  return (
    <Link
      to={`/filmes/${movie.id}`}
      className="group flex flex-col gap-2 rounded-md focus-visible:outline-offset-4"
    >
      <MoviePoster
        title={movie.titulo}
        url={movie.url_poster}
        className="transition duration-200 group-hover:-translate-y-1 group-hover:ring-2 group-hover:ring-accent-400"
      />
      <div className="flex flex-col gap-1 px-0.5">
        <h3 className="line-clamp-2 text-sm leading-snug font-semibold text-ink-100">
          {movie.titulo}
        </h3>
        <div className="flex items-center justify-between gap-2 text-xs text-ink-400">
          <span>{movie.ano_lancamento ?? '—'}</span>
          <span className="flex items-center gap-1">
            <StarRating value={movie.media_estrelas} size="sm" />
            {movie.total_avaliacoes > 0 && (
              <span className="tabular-nums">({movie.total_avaliacoes})</span>
            )}
          </span>
        </div>
      </div>
    </Link>
  )
}
