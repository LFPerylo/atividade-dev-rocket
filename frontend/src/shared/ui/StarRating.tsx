import { clsx } from 'clsx'

import { formatStars, STAR_COUNT, starFill } from '@/domain/rating'
import { StarIcon } from '@/shared/ui/StarIcon'

type StarRatingProps = {
  value: number | null
  size?: 'sm' | 'md' | 'lg'
}

const SIZES = { sm: 'size-3.5', md: 'size-5', lg: 'size-7' }

export function StarRating({ value, size = 'md' }: StarRatingProps) {
  const label = value === null ? 'Sem avaliações' : `Nota ${formatStars(value)} de ${STAR_COUNT}`
  return (
    <span role="img" aria-label={label} className="inline-flex items-center gap-0.5">
      {Array.from({ length: STAR_COUNT }, (_, index) => (
        <span key={index} className={clsx('relative inline-block', SIZES[size])}>
          <StarIcon className="absolute inset-0 text-ink-700" />
          <span
            className="absolute inset-0 overflow-hidden"
            style={{ width: `${starFill(value ?? 0, index) * 100}%` }}
          >
            <StarIcon className={clsx('text-star-400', SIZES[size])} />
          </span>
        </span>
      ))}
    </span>
  )
}
