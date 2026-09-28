import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useDeleteMovie } from '@/features/movies/api'
import { ApiError } from '@/infrastructure/http/client'
import { Button } from '@/shared/ui/Button'
import { ConfirmDialog } from '@/shared/ui/ConfirmDialog'
import { useToast } from '@/shared/ui/toastContext'

type DeleteMovieButtonProps = {
  movieId: string
  title: string
}

export function DeleteMovieButton({ movieId, title }: DeleteMovieButtonProps) {
  const [confirming, setConfirming] = useState(false)
  const deleteMovie = useDeleteMovie()
  const navigate = useNavigate()
  const toast = useToast()

  const confirm = async () => {
    try {
      await deleteMovie.mutateAsync(movieId)
      toast.show('Filme removido')
      navigate('/', { replace: true })
    } catch (error) {
      setConfirming(false)
      toast.show(error instanceof ApiError ? error.message : 'Falha ao remover', 'error')
    }
  }

  return (
    <>
      <Button variant="danger" onClick={() => setConfirming(true)}>
        Remover
      </Button>
      <ConfirmDialog
        open={confirming}
        title={`Remover “${title}”?`}
        description="O filme e todas as suas avaliações serão apagados. Essa ação não pode ser desfeita."
        confirmLabel="Remover filme"
        loading={deleteMovie.isPending}
        onConfirm={confirm}
        onCancel={() => setConfirming(false)}
      />
    </>
  )
}
