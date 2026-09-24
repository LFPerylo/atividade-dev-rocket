import { tokenStorage } from '@/infrastructure/storage/tokenStorage'

describe('tokenStorage', () => {
  it('saves, reads and clears the token', () => {
    tokenStorage.save('abc')
    expect(tokenStorage.read()).toBe('abc')

    tokenStorage.clear()
    expect(tokenStorage.read()).toBeNull()
  })

  it('returns null when storage is unavailable', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked')
    })

    expect(tokenStorage.read()).toBeNull()
    vi.restoreAllMocks()
  })
})
