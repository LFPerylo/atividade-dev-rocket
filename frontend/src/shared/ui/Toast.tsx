import { clsx } from 'clsx'
import { useCallback, useMemo, useState, type ReactNode } from 'react'

import { ToastContext, type ToastTone } from '@/shared/ui/toastContext'

type ToastMessage = {
  id: number
  text: string
  tone: ToastTone
}

const TOAST_DURATION_MS = 4000

export function ToastProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ToastMessage[]>([])

  const show = useCallback((text: string, tone: ToastTone = 'success') => {
    const id = Date.now() + Math.random()
    setMessages((current) => [...current, { id, text, tone }])
    window.setTimeout(
      () => setMessages((current) => current.filter((message) => message.id !== id)),
      TOAST_DURATION_MS,
    )
  }, [])

  const value = useMemo(() => ({ show }), [show])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <output
        aria-live="polite"
        className="pointer-events-none fixed right-4 bottom-4 z-50 flex flex-col gap-2"
      >
        {messages.map((message) => (
          <p
            key={message.id}
            className={clsx(
              'rounded-lg px-4 py-3 text-sm font-medium shadow-xl',
              message.tone === 'success'
                ? 'bg-accent-500 text-ink-950'
                : 'bg-danger-500 text-white',
            )}
          >
            {message.text}
          </p>
        ))}
      </output>
    </ToastContext.Provider>
  )
}
