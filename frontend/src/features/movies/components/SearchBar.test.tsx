import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { SearchBar } from '@/features/movies/components/SearchBar'

describe('SearchBar', () => {
  it('follows external changes to the search term', () => {
    const { rerender } = render(<SearchBar initialValue="nolan" onSearch={vi.fn()} />)

    rerender(<SearchBar initialValue="" onSearch={vi.fn()} />)

    expect(screen.getByRole('searchbox')).toHaveValue('')
  })

  it('keeps typed text while its own debounced search is applied', async () => {
    const onSearch = vi.fn()
    const { rerender } = render(<SearchBar initialValue="" onSearch={onSearch} />)

    await userEvent.type(screen.getByRole('searchbox'), 'ab')
    await vi.waitFor(() => expect(onSearch).toHaveBeenLastCalledWith('ab'))
    await userEvent.type(screen.getByRole('searchbox'), 'c')
    rerender(<SearchBar initialValue="ab" onSearch={onSearch} />)

    expect(screen.getByRole('searchbox')).toHaveValue('abc')
  })
})
