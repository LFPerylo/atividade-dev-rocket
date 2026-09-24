import { zodResolver } from '@hookform/resolvers/zod'
import { Controller, useForm } from 'react-hook-form'
import { z } from 'zod'

import { isValidStarValue } from '@/domain/rating'
import { useAddReview } from '@/features/reviews/api'
import { ApiError } from '@/infrastructure/http/client'
import { Button } from '@/shared/ui/Button'
import { Field, Input, TextArea } from '@/shared/ui/Field'
import { StarInput } from '@/shared/ui/StarInput'
import { useToast } from '@/shared/ui/toastContext'

const STARS_MESSAGE = 'Escolha de 1 a 5 estrelas'

const reviewSchema = z.object({
  estrelas: z
    .number({ error: STARS_MESSAGE })
    .nullable()
    .refine((value) => value !== null && isValidStarValue(value), STARS_MESSAGE),
  nome: z.string().trim().min(1, 'Informe seu nome').max(120, 'Máximo de 120 caracteres'),
  comentario: z
    .string()
    .trim()
    .min(1, 'Escreva sua resenha')
    .max(4000, 'Máximo de 4000 caracteres'),
})

type ReviewValues = z.input<typeof reviewSchema>

const EMPTY_REVIEW: ReviewValues = { estrelas: null, nome: '', comentario: '' }

type ReviewFormProps = {
  movieId: string
  defaultName: string
}

export function ReviewForm({ movieId, defaultName }: ReviewFormProps) {
  const toast = useToast()
  const addReview = useAddReview(movieId)
  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ReviewValues>({
    resolver: zodResolver(reviewSchema),
    defaultValues: { ...EMPTY_REVIEW, nome: defaultName },
  })

  const onSubmit = handleSubmit(async (values) => {
    try {
      await addReview.mutateAsync({
        nome: values.nome.trim(),
        estrelas: values.estrelas ?? 0,
        comentario: values.comentario.trim(),
      })
      toast.show('Avaliação publicada')
      reset({ ...EMPTY_REVIEW, nome: values.nome })
    } catch (error) {
      toast.show(error instanceof ApiError ? error.message : 'Falha ao publicar', 'error')
    }
  })

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      aria-label="Nova avaliação"
      className="flex flex-col gap-4 rounded-xl border border-ink-700 bg-ink-800/60 p-5"
    >
      <h3 className="font-display text-lg font-semibold text-ink-100">Avaliar este filme</h3>
      <div className="flex flex-col gap-1.5">
        <Controller
          control={control}
          name="estrelas"
          render={({ field }) => (
            <StarInput
              value={field.value}
              onChange={field.onChange}
              invalid={Boolean(errors.estrelas)}
              describedBy={errors.estrelas ? 'estrelas-error' : undefined}
            />
          )}
        />
        {errors.estrelas && (
          <p id="estrelas-error" role="alert" className="text-xs text-danger-400">
            {errors.estrelas.message}
          </p>
        )}
      </div>
      <Field id="review-nome" label="Seu nome" error={errors.nome?.message}>
        <Input id="review-nome" invalid={Boolean(errors.nome)} {...register('nome')} />
      </Field>
      <Field id="review-comentario" label="Resenha" error={errors.comentario?.message}>
        <TextArea
          id="review-comentario"
          rows={4}
          placeholder="O que você achou?"
          invalid={Boolean(errors.comentario)}
          {...register('comentario')}
        />
      </Field>
      <Button type="submit" loading={addReview.isPending} className="self-end">
        Publicar avaliação
      </Button>
    </form>
  )
}
