import type { Genre, MovieDetails, Page, Review } from '@/domain/movie'

export const genres: Genre[] = [
  { id: 'g-crime', nome: 'Crime' },
  { id: 'g-drama', nome: 'Drama' },
]

export const cidadeDeDeus: MovieDetails = {
  id: 'm-cdd',
  id_externo: '598',
  titulo: 'Cidade de Deus',
  ano_lancamento: 2002,
  data_lancamento: '2002-08-30',
  duracao_minutos: 130,
  status: 'Lançado',
  sinopse: 'Buscapé cresce em meio à violência.',
  url_poster: null,
  url_backdrop: null,
  generos: genres,
  diretores: ['Fernando Meirelles', 'Kátia Lund'],
  roteiristas: ['Bráulio Mantovani'],
  elenco: ['Alexandre Rodrigues', 'Leandro Firmino'],
  produtoras: ['O2 Filmes'],
  desempenho: {
    orcamento_usd: '3300000.00',
    receita_usd: '30641770.00',
    lucro_usd: '27341770.00',
    popularidade: 40.5,
    nota_tmdb: 8.4,
    votos_tmdb: 7000,
    nota_imdb: 8.6,
    votos_imdb: 800000,
  },
  media_estrelas: 4.5,
  total_avaliacoes: 2,
}

export const ensaio: MovieDetails = {
  ...cidadeDeDeus,
  id: 'm-blind',
  titulo: 'Ensaio sobre a Cegueira',
  ano_lancamento: 2008,
  generos: [{ id: 'g-drama', nome: 'Drama' }],
  diretores: ['Fernando Meirelles'],
  desempenho: null,
  media_estrelas: null,
  total_avaliacoes: 0,
}

export const reviews: Review[] = [
  {
    id: 'r1',
    nome: 'Ana',
    estrelas: 5,
    nota: 10,
    comentario: 'Obra-prima.',
    criado_em: '2026-09-20T12:00:00Z',
  },
  {
    id: 'r2',
    nome: 'Bruno',
    estrelas: 4,
    nota: 8,
    comentario: 'Muito bom.',
    criado_em: '2026-09-19T12:00:00Z',
  },
]

export function pageOf<T>(items: T[], pagina = 1, tamanho = 24): Page<T> {
  return {
    itens: items,
    total: items.length,
    pagina,
    tamanho,
    paginas: Math.ceil(items.length / tamanho),
  }
}
