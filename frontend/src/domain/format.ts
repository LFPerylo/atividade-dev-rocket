const MINUTES_PER_HOUR = 60

const dateFormatter = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' })
const localDateFormatter = new Intl.DateTimeFormat('pt-BR')
const compactFormatter = new Intl.NumberFormat('pt-BR', {
  notation: 'compact',
  maximumFractionDigits: 1,
})
const integerFormatter = new Intl.NumberFormat('pt-BR')

export function formatRuntime(minutes: number | null): string | null {
  if (minutes === null) return null
  const hours = Math.floor(minutes / MINUTES_PER_HOUR)
  const rest = minutes % MINUTES_PER_HOUR
  if (hours === 0) return `${rest}min`
  return rest === 0 ? `${hours}h` : `${hours}h ${rest}min`
}

export function formatDate(value: string): string {
  const isDateOnly = !value.includes('T')
  const formatter = isDateOnly ? dateFormatter : localDateFormatter
  return formatter.format(new Date(value))
}

const NON_BREAKING_SPACE = /\u00a0/g

export function formatCompactNumber(value: number): string {
  return compactFormatter.format(value).replace(NON_BREAKING_SPACE, ' ')
}

export function formatUsd(value: string | null): string | null {
  if (value === null) return null
  return `US$ ${formatCompactNumber(Number(value))}`
}

export function formatReviewCount(count: number): string {
  if (count === 0) return 'Nenhuma avaliação'
  return `${integerFormatter.format(count)} ${count === 1 ? 'avaliação' : 'avaliações'}`
}
