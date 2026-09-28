import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'

import { Pagination } from '@/shared/ui/Pagination'

const meta = {
  title: 'UI/Pagination',
  component: Pagination,
  args: { page: 1, pages: 12, onChange: () => undefined },
} satisfies Meta<typeof Pagination>

export default meta
type Story = StoryObj<typeof meta>

export const Interactive: Story = {
  render: function Render(args) {
    const [page, setPage] = useState(args.page)
    return <Pagination {...args} page={page} onChange={setPage} />
  },
}

export const SinglePage: Story = { args: { pages: 1 } }
