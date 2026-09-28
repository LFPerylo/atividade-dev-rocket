import { Link, useNavigate, useParams } from 'react-router-dom'

import { useMovie, useUpdateMovie } from '@/features/movies/api'
import { MovieForm } from '@/features/movies/components/MovieForm'
import { toFormValues } from '@/features/movies/movieForm'
import { buttonClasses } from '@/shared/ui/buttonStyles'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Skeleton } from '@/shared/ui/Skeleton'
import { useToast } from '@/shared/ui/toastContext'

export function MovieEditPage() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const { data: movie, isPending, isError } = useMovie(id)
  const updateMovie = useUpdateMovie(id)

  if (isPending) return <Skeleton className="mx-auto h-96 max-w-3xl" />
  if (isError) {
    return (
      <EmptyState
        title="Filme não encontrado"
        action={
          <Link to="/" className={buttonClasses('secondary')}>
            Voltar ao catálogo
          </Link>
        }
      />
    )
  }

  return (
    <section className="mx-auto flex max-w-3xl flex-col gap-8">
      <div>
        <p className="text-sm text-ink-400">Editando</p>
        <h1 className="font-display text-4xl font-semibold text-ink-100">{movie.titulo}</h1>
      </div>
      <MovieForm
        initialValues={toFormValues(movie)}
        submitLabel="Salvar alterações"
        onCancel={() => navigate(`/filmes/${id}`)}
        onSubmit={async (input) => {
          await updateMovie.mutateAsync(input)
          toast.show('Filme atualizado')
          navigate(`/filmes/${id}`, { replace: true })
        }}
      />
    </section>
  )
}
