import { render, screen } from '@testing-library/react'

import { StarRating } from '@/shared/ui/StarRating'

describe('StarRating', () => {
  it('announces the average for assistive technologies', () => {
    render(<StarRating value={3.6} />)

    expect(screen.getByRole('img', { name: 'Nota 3,6 de 5' })).toBeInTheDocument()
  })

  it('announces missing ratings', () => {
    render(<StarRating value={null} />)

    expect(screen.getByRole('img', { name: 'Sem avaliações' })).toBeInTheDocument()
  })
})
