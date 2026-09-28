import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type { CatalogFilters } from '@/domain/filters'
import type { Genre, MovieDetails, MovieInput, MovieSummary, Page } from '@/domain/movie'
import { apiClient } from '@/infrastructure/http/apiClient'

export const CATALOG_PAGE_SIZE = 24

export const movieKeys = {
  all: ['movies'] as const,
  list: (filters: CatalogFilters) => ['movies', 'list', filters] as const,
  detail: (id: string) => ['movies', 'detail', id] as const,
  genres: ['genres'] as const,
}

export const moviesApi = {
  list: (filters: CatalogFilters, signal?: AbortSignal) =>
    apiClient.get<Page<MovieSummary>>('/movies', {
      signal,
      query: {
        busca: filters.busca.trim(),
        genero: filters.genero,
        ano_de: filters.anoDe,
        ano_ate: filters.anoAte,
        estrelas_min: filters.estrelasMin,
        ordenar: filters.ordenar,
        ordem: filters.ordem,
        pagina: filters.pagina,
        tamanho: CATALOG_PAGE_SIZE,
      },
    }),
  get: (id: string) => apiClient.get<MovieDetails>(`/movies/${encodeURIComponent(id)}`),
  create: (input: MovieInput) => apiClient.post<MovieDetails>('/movies', input),
  update: (id: string, input: MovieInput) =>
    apiClient.put<MovieDetails>(`/movies/${encodeURIComponent(id)}`, input),
  remove: (id: string) => apiClient.delete(`/movies/${encodeURIComponent(id)}`),
  genres: () => apiClient.get<Genre[]>('/genres'),
}

export function useMovies(filters: CatalogFilters) {
  return useQuery({
    queryKey: movieKeys.list(filters),
    queryFn: ({ signal }) => moviesApi.list(filters, signal),
    placeholderData: keepPreviousData,
  })
}

export function useMovie(id: string) {
  return useQuery({ queryKey: movieKeys.detail(id), queryFn: () => moviesApi.get(id) })
}

export function useGenres() {
  return useQuery({ queryKey: movieKeys.genres, queryFn: moviesApi.genres, staleTime: Infinity })
}

export function useCreateMovie() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: moviesApi.create,
    onSuccess: (movie) => {
      queryClient.setQueryData(movieKeys.detail(movie.id), movie)
      return queryClient.invalidateQueries({ queryKey: movieKeys.all })
    },
  })
}

export function useUpdateMovie(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: MovieInput) => moviesApi.update(id, input),
    onSuccess: (movie) => {
      queryClient.setQueryData(movieKeys.detail(id), movie)
      return queryClient.invalidateQueries({ queryKey: movieKeys.all })
    },
  })
}

export function useDeleteMovie() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: moviesApi.remove,
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: movieKeys.detail(id) })
      return queryClient.invalidateQueries({ queryKey: movieKeys.all })
    },
  })
}
