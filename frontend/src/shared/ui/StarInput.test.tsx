import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { StarInput } from '@/shared/ui/StarInput'

describe('StarInput', () => {
  it('offers every half-star option', () => {
    render(<StarInput value={null} onChange={vi.fn()} />)

    expect(screen.getAllByRole('radio')).toHaveLength(9)
    expect(screen.getByRole('radio', { name: '4,5 estrelas' })).toBeInTheDocument()
  })

  it('reports the selected value', async () => {
    const onChange = vi.fn()
    render(<StarInput value={null} onChange={onChange} />)

    await userEvent.click(screen.getByRole('radio', { name: '3,5 estrelas' }))

    expect(onChange).toHaveBeenCalledWith(3.5)
  })

  it('marks the current value as checked', () => {
    render(<StarInput value={2} onChange={vi.fn()} />)

    expect(screen.getByRole('radio', { name: '2,0 estrelas' })).toBeChecked()
  })
})
