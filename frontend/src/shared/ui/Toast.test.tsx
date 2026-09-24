import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { ToastProvider } from '@/shared/ui/Toast'
import { useToast } from '@/shared/ui/toastContext'

function Trigger() {
  const toast = useToast()
  return <button onClick={() => toast.show('Filme salvo', 'success')}>Salvar</button>
}

describe('Toast', () => {
  it('shows a message and hides it after a while', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    render(
      <ToastProvider>
        <Trigger />
      </ToastProvider>,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))
    expect(screen.getByRole('status')).toHaveTextContent('Filme salvo')

    act(() => vi.advanceTimersByTime(5000))
    expect(screen.queryByText('Filme salvo')).not.toBeInTheDocument()
    vi.useRealTimers()
  })
})
