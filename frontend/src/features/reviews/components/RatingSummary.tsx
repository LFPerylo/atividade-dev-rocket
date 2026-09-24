import { formatReviewCount } from '@/domain/format'
import { formatStars } from '@/domain/rating'
import { StarRating } from '@/shared/ui/StarRating'

type RatingSummaryProps = {
  average: number | null
  count: number
}

export function RatingSummary({ average, count }: RatingSummaryProps) {
  return (
    <section
      aria-label="Média das avaliações"
      className="flex items-center gap-4 rounded-xl border border-ink-700 bg-ink-800/60 px-5 py-4"
    >
      <span className="font-display text-5xl font-semibold text-ink-100 tabular-nums">
        {formatStars(average)}
      </span>
      <div className="flex flex-col gap-1">
        <StarRating value={average} size="lg" />
        <span className="text-sm text-ink-400">{formatReviewCount(count)}</span>
      </div>
    </section>
  )
}
