import { formatStars, isValidStarValue, STAR_VALUES, starFill } from '@/domain/rating'

describe('rating', () => {
  it('offers half-star values from 1 to 5', () => {
    expect(STAR_VALUES).toEqual([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
  })

  it.each([
    [4.5, true],
    [1, true],
    [0.5, false],
    [5.5, false],
    [3.2, false],
  ])('validates %s as star value: %s', (value, expected) => {
    expect(isValidStarValue(value)).toBe(expected)
  })

  it('formats averages in Brazilian notation', () => {
    expect(formatStars(4.5)).toBe('4,5')
    expect(formatStars(3)).toBe('3,0')
    expect(formatStars(null)).toBe('–')
  })

  it.each([
    [3.6, 0, 1],
    [3.6, 3, 0.6],
    [3.6, 4, 0],
  ])('computes fill of star index for %s at %s as %s', (average, index, fill) => {
    expect(starFill(average, index)).toBeCloseTo(fill)
  })
})
