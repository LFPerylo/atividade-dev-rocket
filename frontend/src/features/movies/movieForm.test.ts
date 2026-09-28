import {
  EMPTY_MOVIE_FORM,
  movieFormSchema,
  toFormValues,
  toMovieInput,
} from '@/features/movies/movieForm'
import { cidadeDeDeus } from '@/test/fixtures'

describe('movie form mapping', () => {
  it('converts form values into api payload', () => {
    const input = toMovieInput({
      ...EMPTY_MOVIE_FORM,
      titulo: '  Central do Brasil ',
      diretores: 'Walter Salles,  , Outro Nome ',
      generos: ['g-drama'],
      ano_lancamento: '1998',
      duracao_minutos: '113',
      sinopse: ' Dora escreve cartas. ',
    })

    expect(input).toEqual({
      titulo: 'Central do Brasil',
      diretores: ['Walter Salles', 'Outro Nome'],
      generos: ['g-drama'],
      ano_lancamento: 1998,
      data_lancamento: null,
      duracao_minutos: 113,
      sinopse: 'Dora escreve cartas.',
      url_poster: null,
      url_backdrop: null,
    })
  })

  it('converts movie details into form values', () => {
    const values = toFormValues(cidadeDeDeus)

    expect(values).toMatchObject({
      titulo: 'Cidade de Deus',
      diretores: 'Fernando Meirelles, Kátia Lund',
      generos: ['g-crime', 'g-drama'],
      ano_lancamento: '2002',
      data_lancamento: '2002-08-30',
      duracao_minutos: '130',
      url_poster: '',
    })
  })

  it.each([
    [{ titulo: ' ' }, 'titulo', 'Informe o título'],
    [{ ano_lancamento: '1500' }, 'ano_lancamento', 'Ano entre 1870 e 2100'],
    [{ duracao_minutos: '-1' }, 'duracao_minutos', 'Duração não pode ser negativa'],
    [{ url_poster: 'não é url' }, 'url_poster', 'Informe uma URL válida'],
    [
      { ano_lancamento: '2001', data_lancamento: '2002-08-30' },
      'ano_lancamento',
      'Ano difere da data de lançamento',
    ],
  ])('rejects %o', (overrides, path, message) => {
    const result = movieFormSchema.safeParse({ ...EMPTY_MOVIE_FORM, titulo: 'X', ...overrides })

    expect(result.success).toBe(false)
    expect(result.error?.issues).toContainEqual(expect.objectContaining({ path: [path], message }))
  })
})
