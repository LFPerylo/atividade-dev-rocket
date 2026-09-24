import { act, renderHook } from '@testing-library/react'

import { useDebouncedCallback } from '@/shared/hooks/useDebouncedCallback'

describe('useDebouncedCallback', () => {
  it('calls only the last invocation after the delay', () => {
    vi.useFakeTimers()
    const callback = vi.fn()
    const { result } = renderHook(() => useDebouncedCallback(callback, 300))

    act(() => {
      result.current('a')
      result.current('ab')
      vi.advanceTimersByTime(299)
    })
    expect(callback).not.toHaveBeenCalled()

    act(() => vi.advanceTimersByTime(1))
    expect(callback).toHaveBeenCalledExactlyOnceWith('ab')
    vi.useRealTimers()
  })
})
