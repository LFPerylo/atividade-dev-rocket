import type { Meta, StoryObj } from '@storybook/react-vite'

import { Button } from '@/shared/ui/Button'

const meta = {
  title: 'UI/Button',
  component: Button,
  args: { children: 'Cadastrar filme' },
  argTypes: {
    variant: { control: 'inline-radio', options: ['primary', 'secondary', 'ghost', 'danger'] },
  },
} satisfies Meta<typeof Button>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {}
export const Secondary: Story = { args: { variant: 'secondary', children: 'Editar' } }
export const Ghost: Story = { args: { variant: 'ghost', children: 'Cancelar' } }
export const Danger: Story = { args: { variant: 'danger', children: 'Remover' } }
export const Loading: Story = { args: { loading: true, children: 'Salvando' } }
