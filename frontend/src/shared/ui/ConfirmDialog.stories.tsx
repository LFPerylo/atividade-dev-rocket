import type { Meta, StoryObj } from '@storybook/react-vite'

import { ConfirmDialog } from '@/shared/ui/ConfirmDialog'

const meta = {
  title: 'UI/ConfirmDialog',
  component: ConfirmDialog,
  parameters: { layout: 'fullscreen' },
  args: {
    open: true,
    title: 'Remover “Oppenheimer”?',
    description: 'O filme e todas as suas avaliações serão apagados.',
    confirmLabel: 'Remover filme',
    onConfirm: () => undefined,
    onCancel: () => undefined,
  },
} satisfies Meta<typeof ConfirmDialog>

export default meta
type Story = StoryObj<typeof meta>

export const Open: Story = {}
export const Loading: Story = { args: { loading: true } }
