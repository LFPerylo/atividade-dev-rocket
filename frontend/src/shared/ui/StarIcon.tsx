import { StarIcon as PhosphorStar } from '@phosphor-icons/react'

export function StarIcon({ className }: { className?: string }) {
  return <PhosphorStar weight="fill" aria-hidden="true" className={className} />
}
