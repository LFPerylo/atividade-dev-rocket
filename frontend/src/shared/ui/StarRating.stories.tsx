import type { Meta, StoryObj } from '@storybook/react-vite'

import { StarRating } from '@/shared/ui/StarRating'

const meta = {
  title: 'UI/StarRating',
  component: StarRating,
  args: { value: 3.6, size: 'md' },
  argTypes: {
    value: { control: { type: 'range', min: 0, max: 5, step: 0.1 } },
    size: { control: 'inline-radio', options: ['sm', 'md', 'lg'] },
  },
} satisfies Meta<typeof StarRating>

export default meta
type Story = StoryObj<typeof meta>

export const Fractional: Story = {}
export const Perfect: Story = { args: { value: 5, size: 'lg' } }
export const WithoutReviews: Story = { args: { value: null } }
