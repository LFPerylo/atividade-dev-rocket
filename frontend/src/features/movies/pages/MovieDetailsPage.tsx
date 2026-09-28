import { Link, useLocation, useParams } from 'react-router-dom'

import { formatRuntime } from '@/domain/format'
import { useAuth } from '@/features/auth/authContext'
import { useMovie } from '@/features/movies/api'
import { DeleteMovieButton } from '@/features/movies/components/DeleteMovieButton'
import { MovieFacts } from '@/features/movies/components/MovieFacts'
import { MoviePoster } from '@/features/movies/components/MoviePoster'
import { RatingSummary } from '@/features/reviews/components/RatingSummary'
import { ReviewForm } from '@/features/reviews/components/ReviewForm'
import { ReviewList } from '@/features/reviews/components/ReviewList'
import { ApiError } from '@/infrastructure/http/client'
import { buttonClasses } from '@/shared/ui/buttonStyles'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Skeleton } from '@/shared/ui/Skeleton'

const NOT_FOUND = 404

export function MovieDetailsPage() {
  const { id = '' } = useParams()
  const location = useLocation()
  const { status, admin } = useAuth()
  const { data: movie, isPending, error } = useMovie(id)

  if (isPending) {
    return (
      <div className="grid gap-8 md:grid-cols-[16rem_1fr]">
        <Skeleton className="aspect-[2/3]" />
        <div className="flex flex-col gap-4">
          <Skeleton className="h-10 w-2/3" />
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-32" />
        </div>
      </div>
    )
  }
  if (error) {
    const notFound = error instanceof ApiError && error.status === NOT_FOUND
    return (
      <EmptyState
        title={notFound ? 'Filme não encontrado' : 'Não foi possível carregar o filme'}
        action={
          <Link to="/" className={buttonClasses('secondary')}>
            Voltar ao catálogo
          </Link>
        }
      />
    )
  }

  const isAdmin = status === 'authenticated'
  const runtime = formatRuntime(movie.duracao_minutos)
  const loginLink = `/login?next=${encodeURIComponent(location.pathname)}`

  return (
    <article className="flex flex-col gap-12">
      <div className="relative -mx-4 -mt-8 overflow-hidden sm:-mx-6">
        {movie.url_backdrop && (
          <img
            src={movie.url_backdrop}
            alt=""
            className="absolute inset-0 size-full object-cover opacity-30"
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-ink-900/80 to-ink-900/40" />
        <div className="relative grid gap-8 px-4 pt-10 pb-6 sm:px-6 md:grid-cols-[16rem_1fr]">
          <MoviePoster
            title={movie.titulo}
            url={movie.url_poster}
            className="mx-auto w-48 shadow-2xl md:w-full"
          />
          <div className="flex flex-col gap-5">
            <div className="flex flex-col gap-2">
              <h1 className="font-display text-4xl font-semibold text-ink-100 md:text-5xl">
                {movie.titulo}
              </h1>
              <p className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-ink-400">
                {movie.ano_lancamento && <span>{movie.ano_lancamento}</span>}
                {runtime && <span>{runtime}</span>}
                {movie.diretores.length > 0 && (
                  <span>
                    Direção{' '}
                    <strong className="font-semibold text-ink-100">
                      {movie.diretores.join(', ')}
                    </strong>
                  </span>
                )}
              </p>
              {movie.generos.length > 0 && (
                <ul aria-label="Gêneros" className="flex flex-wrap gap-2">
                  {movie.generos.map((genre) => (
                    <li
                      key={genre.id}
                      className="rounded-full border border-ink-600 px-3 py-0.5 text-xs text-ink-200"
                    >
                      {genre.nome}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <RatingSummary average={movie.media_estrelas} count={movie.total_avaliacoes} />
            {movie.sinopse && (
              <p className="max-w-3xl leading-relaxed text-ink-200">{movie.sinopse}</p>
            )}
            {isAdmin && (
              <div className="flex gap-3">
                <Link to={`/filmes/${movie.id}/editar`} className={buttonClasses('secondary')}>
                  Editar
                </Link>
                <DeleteMovieButton movieId={movie.id} title={movie.titulo} />
              </div>
            )}
          </div>
        </div>
      </div>

      <MovieFacts movie={movie} />

      <section aria-labelledby="reviews-title" className="grid gap-8 lg:grid-cols-[1fr_24rem]">
        <div className="flex flex-col gap-4">
          <h2 id="reviews-title" className="font-display text-2xl font-semibold text-ink-100">
            Avaliações
          </h2>
          <ReviewList movieId={movie.id} />
        </div>
        <aside className="lg:sticky lg:top-24 lg:self-start">
          {isAdmin ? (
            <ReviewForm movieId={movie.id} defaultName={admin?.nome ?? ''} />
          ) : (
            <div className="rounded-xl border border-ink-700 bg-ink-800/60 p-5 text-sm text-ink-400">
              Quer registrar uma avaliação?{' '}
              <Link to={loginLink} className="font-semibold text-accent-400 hover:underline">
                Entre como administrador
              </Link>
              .
            </div>
          )}
        </aside>
      </section>
    </article>
  )
}
