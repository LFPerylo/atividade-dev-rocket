import type { MovieSummary } from '@/domain/movie'
import { MovieCard } from '@/features/movies/components/MovieCard'
import { Skeleton } from '@/shared/ui/Skeleton'

const GRID_CLASSES = 'grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6'
const SKELETON_COUNT = 12

export function MovieGrid({ movies }: { movies: MovieSummary[] }) {
  return (
    <ul className={GRID_CLASSES}>
      {movies.map((movie) => (
        <li key={movie.id}>
          <MovieCard movie={movie} />
        </li>
      ))}
    </ul>
  )
}

export function MovieGridSkeleton() {
  return (
    <div className={GRID_CLASSES} aria-label="Carregando filmes">
      {Array.from({ length: SKELETON_COUNT }, (_, index) => (
        <div key={index} className="flex flex-col gap-2">
          <Skeleton className="aspect-[2/3]" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      ))}
    </div>
  )
}
