import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'

import { StarInput } from '@/shared/ui/StarInput'

const meta = {
  title: 'UI/StarInput',
  component: StarInput,
  args: { value: null, onChange: () => undefined },
} satisfies Meta<typeof StarInput>

export default meta
type Story = StoryObj<typeof meta>

export const Interactive: Story = {
  render: function Render(args) {
    const [value, setValue] = useState<number | null>(args.value)
    return <StarInput {...args} value={value} onChange={setValue} />
  },
}

export const Preselected: Story = { args: { value: 4.5 } }
export const Invalid: Story = { args: { invalid: true } }
