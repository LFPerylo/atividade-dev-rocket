export const MIN_STARS = 1
export const MAX_STARS = 5
export const STAR_STEP = 0.5
export const STAR_COUNT = 5

export const STAR_VALUES: number[] = Array.from(
  { length: (MAX_STARS - MIN_STARS) / STAR_STEP + 1 },
  (_, index) => MIN_STARS + index * STAR_STEP,
)

const starsFormatter = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})

export function isValidStarValue(value: number): boolean {
  return STAR_VALUES.includes(value)
}

export function formatStars(average: number | null): string {
  return average === null ? '–' : starsFormatter.format(average)
}

export function starFill(average: number, index: number): number {
  return Math.min(Math.max(average - index, 0), 1)
}
