import { render, screen } from '@testing-library/react'

import { RatingSummary } from '@/features/reviews/components/RatingSummary'

describe('RatingSummary', () => {
  it('shows the average when there are reviews', () => {
    render(<RatingSummary average={4.5} count={2} />)

    expect(screen.getByText('4,5')).toBeInTheDocument()
    expect(screen.getByText('2 avaliações')).toBeInTheDocument()
  })

  it('omits the number when the movie has no rating yet', () => {
    render(<RatingSummary average={null} count={0} />)

    const summary = screen.getByRole('region', { name: 'Média das avaliações' })
    expect(summary).toHaveTextContent('Nenhuma avaliação')
    expect(summary).not.toHaveTextContent('-')
  })
})
