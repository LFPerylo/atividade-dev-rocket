import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type { Page, Review, ReviewInput } from '@/domain/movie'
import { movieKeys } from '@/features/movies/api'
import { apiClient } from '@/infrastructure/http/apiClient'

export const REVIEWS_PAGE_SIZE = 5

export const reviewKeys = {
  list: (movieId: string, page: number) => ['reviews', movieId, page] as const,
  movie: (movieId: string) => ['reviews', movieId] as const,
}

export const reviewsApi = {
  list: (movieId: string, page: number) =>
    apiClient.get<Page<Review>>(`/movies/${encodeURIComponent(movieId)}/reviews`, {
      query: { pagina: page, tamanho: REVIEWS_PAGE_SIZE },
    }),
  add: (movieId: string, input: ReviewInput) =>
    apiClient.post<Review>(`/movies/${encodeURIComponent(movieId)}/reviews`, input),
}

export function useReviews(movieId: string, page: number) {
  return useQuery({
    queryKey: reviewKeys.list(movieId, page),
    queryFn: () => reviewsApi.list(movieId, page),
    placeholderData: keepPreviousData,
  })
}

export function useAddReview(movieId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: ReviewInput) => reviewsApi.add(movieId, input),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: reviewKeys.movie(movieId) }),
        queryClient.invalidateQueries({ queryKey: movieKeys.all }),
      ]),
  })
}
