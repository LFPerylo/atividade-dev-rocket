import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactElement } from 'react'

import { DEFAULT_FILTERS } from '@/domain/filters'
import { FiltersPanel } from '@/features/movies/components/FiltersPanel'

const queryClient = new QueryClient()
const withQuery = (element: ReactElement) => (
  <QueryClientProvider client={queryClient}>{element}</QueryClientProvider>
)

describe('FiltersPanel', () => {
  it('applies typed year when leaving the field', async () => {
    const onChange = vi.fn()
    render(withQuery(<FiltersPanel filters={DEFAULT_FILTERS} onChange={onChange} />))

    await userEvent.type(screen.getByLabelText('Ano de'), '1990')
    await userEvent.tab()

    expect(onChange).toHaveBeenCalledWith({ anoDe: 1990 })
  })

  it('follows external changes to year filters', () => {
    const filters = { ...DEFAULT_FILTERS, anoDe: 1990, anoAte: 2000 }
    const { rerender } = render(withQuery(<FiltersPanel filters={filters} onChange={vi.fn()} />))

    rerender(withQuery(<FiltersPanel filters={DEFAULT_FILTERS} onChange={vi.fn()} />))

    expect(screen.getByLabelText('Ano de')).toHaveValue(null)
    expect(screen.getByLabelText('Ano até')).toHaveValue(null)
  })
})
