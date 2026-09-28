import { zodResolver } from '@hookform/resolvers/zod'
import { clsx } from 'clsx'
import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'

import type { MovieInput } from '@/domain/movie'
import { useGenres } from '@/features/movies/api'
import {
  EMPTY_MOVIE_FORM,
  movieFormSchema,
  type MovieFormValues,
  toMovieInput,
} from '@/features/movies/movieForm'
import { ApiError } from '@/infrastructure/http/client'
import { Button } from '@/shared/ui/Button'
import { Field, Input, TextArea } from '@/shared/ui/Field'

type MovieFormProps = {
  initialValues?: MovieFormValues
  submitLabel: string
  onSubmit: (input: MovieInput) => Promise<void>
  onCancel: () => void
}

export function MovieForm({
  initialValues = EMPTY_MOVIE_FORM,
  submitLabel,
  onSubmit,
  onCancel,
}: MovieFormProps) {
  const { data: genres = [] } = useGenres()
  const [serverError, setServerError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<MovieFormValues>({
    resolver: zodResolver(movieFormSchema),
    defaultValues: initialValues,
  })
  const selectedGenres = useWatch({ control, name: 'generos' })

  const submit = handleSubmit(async (values) => {
    setServerError(null)
    try {
      await onSubmit(toMovieInput(values))
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : 'Não foi possível salvar')
    }
  })

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-6">
      <div className="grid gap-5 md:grid-cols-2">
        <div className="md:col-span-2">
          <Field id="titulo" label="Título" error={errors.titulo?.message}>
            <Input id="titulo" invalid={Boolean(errors.titulo)} {...register('titulo')} />
          </Field>
        </div>
        <Field id="diretores" label="Diretores" hint="Separe vários nomes por vírgula">
          <Input id="diretores" placeholder="Ex.: Walter Salles" {...register('diretores')} />
        </Field>
        <div className="grid grid-cols-3 gap-3">
          <Field
            id="ano_lancamento"
            label="Ano de lançamento"
            error={errors.ano_lancamento?.message}
          >
            <Input
              id="ano_lancamento"
              inputMode="numeric"
              invalid={Boolean(errors.ano_lancamento)}
              {...register('ano_lancamento')}
            />
          </Field>
          <Field id="data_lancamento" label="Data" error={errors.data_lancamento?.message}>
            <Input id="data_lancamento" type="date" {...register('data_lancamento')} />
          </Field>
          <Field id="duracao_minutos" label="Duração (min)" error={errors.duracao_minutos?.message}>
            <Input
              id="duracao_minutos"
              inputMode="numeric"
              invalid={Boolean(errors.duracao_minutos)}
              {...register('duracao_minutos')}
            />
          </Field>
        </div>
        <fieldset className="flex flex-col gap-2 md:col-span-2">
          <legend className="mb-1.5 text-sm font-medium text-ink-200">Gêneros</legend>
          <div className="flex flex-wrap gap-2">
            {genres.map((genre) => {
              const checked = selectedGenres.includes(genre.id)
              return (
                <label
                  key={genre.id}
                  className={clsx(
                    'cursor-pointer rounded-full border px-3 py-1 text-sm transition-colors has-focus-visible:outline-2 has-focus-visible:outline-accent-400',
                    checked
                      ? 'border-accent-400 bg-accent-500/15 text-accent-400'
                      : 'border-ink-700 text-ink-200 hover:border-ink-600',
                  )}
                >
                  <input
                    type="checkbox"
                    value={genre.id}
                    className="sr-only"
                    {...register('generos')}
                  />
                  {genre.nome}
                </label>
              )
            })}
          </div>
        </fieldset>
        <div className="md:col-span-2">
          <Field id="sinopse" label="Sinopse" error={errors.sinopse?.message}>
            <TextArea
              id="sinopse"
              rows={5}
              invalid={Boolean(errors.sinopse)}
              {...register('sinopse')}
            />
          </Field>
        </div>
        <Field id="url_poster" label="URL do pôster" error={errors.url_poster?.message}>
          <Input
            id="url_poster"
            type="url"
            placeholder="https://…"
            invalid={Boolean(errors.url_poster)}
            {...register('url_poster')}
          />
        </Field>
        <Field
          id="url_backdrop"
          label="URL da imagem de fundo"
          error={errors.url_backdrop?.message}
        >
          <Input
            id="url_backdrop"
            type="url"
            placeholder="https://…"
            invalid={Boolean(errors.url_backdrop)}
            {...register('url_backdrop')}
          />
        </Field>
      </div>
      {serverError && (
        <p role="alert" className="rounded-md bg-danger-500/15 px-3 py-2 text-sm text-danger-400">
          {serverError}
        </p>
      )}
      <div className="flex justify-end gap-3">
        <Button variant="ghost" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={isSubmitting}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}
