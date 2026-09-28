import { useNavigate } from 'react-router-dom'

import { useCreateMovie } from '@/features/movies/api'
import { MovieForm } from '@/features/movies/components/MovieForm'
import { useToast } from '@/shared/ui/toastContext'

export function MovieCreatePage() {
  const navigate = useNavigate()
  const toast = useToast()
  const createMovie = useCreateMovie()

  return (
    <section className="mx-auto flex max-w-3xl flex-col gap-8">
      <h1 className="font-display text-4xl font-semibold text-ink-100">Novo filme</h1>
      <MovieForm
        submitLabel="Cadastrar filme"
        onCancel={() => navigate(-1)}
        onSubmit={async (input) => {
          const movie = await createMovie.mutateAsync(input)
          toast.show('Filme cadastrado')
          navigate(`/filmes/${movie.id}`, { replace: true })
        }}
      />
    </section>
  )
}
