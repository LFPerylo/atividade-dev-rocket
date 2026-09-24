import type { Meta, StoryObj } from '@storybook/react-vite'
import { MemoryRouter } from 'react-router-dom'

import { MovieCard } from '@/features/movies/components/MovieCard'

const meta = {
  title: 'Filmes/MovieCard',
  component: MovieCard,
  decorators: [
    (Story) => (
      <MemoryRouter>
        <div className="w-44">
          <Story />
        </div>
      </MemoryRouter>
    ),
  ],
  args: {
    movie: {
      id: 'm1',
      titulo: 'Oppenheimer',
      ano_lancamento: 2023,
      url_poster: 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg',
      generos: [{ id: 'g1', nome: 'Drama' }],
      diretores: ['Christopher Nolan'],
      media_estrelas: 4.3,
      total_avaliacoes: 12,
    },
  },
} satisfies Meta<typeof MovieCard>

export default meta
type Story = StoryObj<typeof meta>

export const WithPoster: Story = {}

export const WithoutPoster: Story = {
  args: {
    movie: {
      id: 'm2',
      titulo: 'Um Filme Sem Pôster',
      ano_lancamento: null,
      url_poster: null,
      generos: [],
      diretores: [],
      media_estrelas: null,
      total_avaliacoes: 0,
    },
  },
}
