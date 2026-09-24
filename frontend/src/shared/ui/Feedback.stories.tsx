import type { Meta, StoryObj } from '@storybook/react-vite'

import { Button } from '@/shared/ui/Button'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Skeleton } from '@/shared/ui/Skeleton'
import { ToastProvider } from '@/shared/ui/Toast'
import { useToast } from '@/shared/ui/toastContext'

const meta = {
  title: 'UI/Feedback',
  component: EmptyState,
  args: {
    title: 'Nenhum filme encontrado',
    description: 'Tente outro termo de busca ou ajuste os filtros.',
  },
} satisfies Meta<typeof EmptyState>

export default meta
type Story = StoryObj<typeof meta>

export const Empty: Story = {}

export const Loading: Story = {
  render: () => (
    <div className="flex w-48 flex-col gap-2">
      <Skeleton className="aspect-[2/3]" />
      <Skeleton className="h-4 w-3/4" />
    </div>
  ),
}

function ToastDemo() {
  const toast = useToast()
  return (
    <div className="flex gap-3">
      <Button onClick={() => toast.show('Filme cadastrado')}>Sucesso</Button>
      <Button variant="danger" onClick={() => toast.show('Falha ao salvar', 'error')}>
        Erro
      </Button>
    </div>
  )
}

export const Toasts: Story = {
  render: () => (
    <ToastProvider>
      <ToastDemo />
    </ToastProvider>
  ),
}
