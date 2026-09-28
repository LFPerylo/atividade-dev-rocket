import { useState } from 'react'

import { formatDate } from '@/domain/format'
import { REVIEWS_PAGE_SIZE, useReviews } from '@/features/reviews/api'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Pagination } from '@/shared/ui/Pagination'
import { Skeleton } from '@/shared/ui/Skeleton'
import { StarRating } from '@/shared/ui/StarRating'

export function ReviewList({ movieId }: { movieId: string }) {
  const [page, setPage] = useState(1)
  const { data, isPending, isError } = useReviews(movieId, page)

  if (isPending) {
    return (
      <div className="flex flex-col gap-3">
        {Array.from({ length: REVIEWS_PAGE_SIZE }, (_, index) => (
          <Skeleton key={index} className="h-20" />
        ))}
      </div>
    )
  }
  if (isError) return <EmptyState title="Não foi possível carregar as avaliações" />
  if (data.itens.length === 0) {
    return <EmptyState title="Ainda sem avaliações" description="Seja o primeiro a avaliar." />
  }

  return (
    <div className="flex flex-col gap-6">
      <ul aria-label="Avaliações" className="flex flex-col divide-y divide-ink-800">
        {data.itens.map((review) => (
          <li key={review.id} className="flex flex-col gap-2 py-4">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
              <span className="font-semibold text-ink-100">{review.nome}</span>
              <StarRating value={review.estrelas} size="sm" />
              <time dateTime={review.criado_em} className="text-xs text-ink-600">
                {formatDate(review.criado_em)}
              </time>
            </div>
            <p className="text-sm leading-relaxed whitespace-pre-line text-ink-200">
              {review.comentario}
            </p>
          </li>
        ))}
      </ul>
      <Pagination page={data.pagina} pages={data.paginas} onChange={setPage} />
    </div>
  )
}
