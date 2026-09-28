import { z } from 'zod'

import type { MovieDetails, MovieInput } from '@/domain/movie'

const MIN_YEAR = 1870
const MAX_YEAR = 2100
const DIRECTOR_SEPARATOR = ','

const optionalInteger = (check: (value: number) => boolean, message: string) =>
  z
    .string()
    .trim()
    .refine(
      (value) => value === '' || (Number.isInteger(Number(value)) && check(Number(value))),
      message,
    )

const optionalUrl = z
  .string()
  .trim()
  .refine((value) => value === '' || URL.canParse(value), 'Informe uma URL válida')

export const movieFormSchema = z
  .object({
    titulo: z.string().trim().min(1, 'Informe o título').max(500, 'Máximo de 500 caracteres'),
    diretores: z.string(),
    generos: z.array(z.string()),
    ano_lancamento: optionalInteger(
      (year) => year >= MIN_YEAR && year <= MAX_YEAR,
      `Ano entre ${MIN_YEAR} e ${MAX_YEAR}`,
    ),
    data_lancamento: z.string(),
    duracao_minutos: optionalInteger((minutes) => minutes >= 0, 'Duração não pode ser negativa'),
    sinopse: z.string().max(4000, 'Máximo de 4000 caracteres'),
    url_poster: optionalUrl,
    url_backdrop: optionalUrl,
  })
  .refine(
    ({ ano_lancamento, data_lancamento }) =>
      !ano_lancamento || !data_lancamento || data_lancamento.startsWith(ano_lancamento),
    { path: ['ano_lancamento'], message: 'Ano difere da data de lançamento' },
  )

export type MovieFormValues = z.input<typeof movieFormSchema>

export const EMPTY_MOVIE_FORM: MovieFormValues = {
  titulo: '',
  diretores: '',
  generos: [],
  ano_lancamento: '',
  data_lancamento: '',
  duracao_minutos: '',
  sinopse: '',
  url_poster: '',
  url_backdrop: '',
}

const emptyToNull = (value: string) => value.trim() || null
const toNumberOrNull = (value: string) => (value.trim() ? Number(value) : null)

export function toMovieInput(values: MovieFormValues): MovieInput {
  return {
    titulo: values.titulo.trim(),
    diretores: values.diretores
      .split(DIRECTOR_SEPARATOR)
      .map((name) => name.trim())
      .filter(Boolean),
    generos: values.generos,
    ano_lancamento: toNumberOrNull(values.ano_lancamento),
    data_lancamento: emptyToNull(values.data_lancamento),
    duracao_minutos: toNumberOrNull(values.duracao_minutos),
    sinopse: emptyToNull(values.sinopse),
    url_poster: emptyToNull(values.url_poster),
    url_backdrop: emptyToNull(values.url_backdrop),
  }
}

export function toFormValues(movie: MovieDetails): MovieFormValues {
  return {
    titulo: movie.titulo,
    diretores: movie.diretores.join(`${DIRECTOR_SEPARATOR} `),
    generos: movie.generos.map((genre) => genre.id),
    ano_lancamento: movie.ano_lancamento?.toString() ?? '',
    data_lancamento: movie.data_lancamento ?? '',
    duracao_minutos: movie.duracao_minutos?.toString() ?? '',
    sinopse: movie.sinopse ?? '',
    url_poster: movie.url_poster ?? '',
    url_backdrop: movie.url_backdrop ?? '',
  }
}
