export type Genre = {
  id: string
  nome: string
}

export type MovieSummary = {
  id: string
  titulo: string
  ano_lancamento: number | null
  url_poster: string | null
  generos: Genre[]
  diretores: string[]
  media_estrelas: number | null
  total_avaliacoes: number
}

export type Performance = {
  orcamento_usd: string | null
  receita_usd: string | null
  lucro_usd: string | null
  popularidade: number | null
  nota_tmdb: number | null
  votos_tmdb: number | null
  nota_imdb: number | null
  votos_imdb: number | null
}

export type MovieDetails = MovieSummary & {
  id_externo: string
  data_lancamento: string | null
  duracao_minutos: number | null
  status: string | null
  sinopse: string | null
  url_backdrop: string | null
  roteiristas: string[]
  elenco: string[]
  produtoras: string[]
  desempenho: Performance | null
}

export type Review = {
  id: string
  nome: string
  estrelas: number
  nota: number
  comentario: string
  criado_em: string
}

export type Page<T> = {
  itens: T[]
  total: number
  pagina: number
  tamanho: number
  paginas: number
}

export type MovieInput = {
  titulo: string
  diretores: string[]
  generos: string[]
  ano_lancamento: number | null
  data_lancamento: string | null
  duracao_minutos: number | null
  sinopse: string | null
  url_poster: string | null
  url_backdrop: string | null
}

export type ReviewInput = {
  nome: string
  estrelas: number
  comentario: string
}

export type Admin = {
  id: string
  email: string
  nome: string
}
