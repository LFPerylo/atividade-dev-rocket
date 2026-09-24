import { createContext, useContext } from 'react'

export type ToastTone = 'success' | 'error'

export type ToastContextValue = {
  show: (text: string, tone?: ToastTone) => void
}

export const ToastContext = createContext<ToastContextValue | null>(null)

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast deve ser usado dentro de ToastProvider')
  return context
}
