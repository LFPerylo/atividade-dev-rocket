import {
  formatCompactNumber,
  formatDate,
  formatReviewCount,
  formatRuntime,
  formatUsd,
} from '@/domain/format'

describe('format', () => {
  it.each([
    [130, '2h 10min'],
    [90, '1h 30min'],
    [45, '45min'],
    [120, '2h'],
    [0, null],
    [null, null],
  ])('formats runtime %s as %s', (minutes, expected) => {
    expect(formatRuntime(minutes)).toBe(expected)
  })

  it('formats ISO dates in Brazilian format', () => {
    expect(formatDate('2002-08-30')).toBe('30/08/2002')
    expect(formatDate('2026-09-24T15:30:00Z')).toBe('24/09/2026')
  })

  it('formats dollars compactly', () => {
    expect(formatUsd('30641770.00')).toBe('US$ 30,6 mi')
    expect(formatUsd(null)).toBeNull()
  })

  it('formats large counts compactly', () => {
    expect(formatCompactNumber(800000)).toBe('800 mil')
  })

  it('pluralizes review counts', () => {
    expect(formatReviewCount(0)).toBe('Nenhuma avaliação')
    expect(formatReviewCount(1)).toBe('1 avaliação')
    expect(formatReviewCount(1234)).toBe('1.234 avaliações')
  })
})
