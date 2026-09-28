import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Pagination } from '@/shared/ui/Pagination'

describe('Pagination', () => {
  it('shows current position', () => {
    render(<Pagination page={2} pages={10} onChange={vi.fn()} />)

    expect(screen.getByText('Página 2 de 10')).toBeInTheDocument()
  })

  it('navigates to previous and next pages', async () => {
    const onChange = vi.fn()
    render(<Pagination page={2} pages={10} onChange={onChange} />)

    await userEvent.click(screen.getByRole('button', { name: 'Próxima página' }))
    await userEvent.click(screen.getByRole('button', { name: 'Página anterior' }))

    expect(onChange.mock.calls).toEqual([[3], [1]])
  })

  it('disables navigation at the edges', () => {
    render(<Pagination page={1} pages={1} onChange={vi.fn()} />)

    expect(screen.getByRole('button', { name: 'Página anterior' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Próxima página' })).toBeDisabled()
  })

  it('renders nothing without pages', () => {
    const { container } = render(<Pagination page={1} pages={0} onChange={vi.fn()} />)

    expect(container).toBeEmptyDOMElement()
  })
})
