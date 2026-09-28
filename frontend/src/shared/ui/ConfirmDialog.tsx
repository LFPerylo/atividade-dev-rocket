import { useEffect, useId } from 'react'

import { Button } from '@/shared/ui/Button'

type ConfirmDialogProps = {
  open: boolean
  title: string
  description?: string
  confirmLabel: string
  loading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel,
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const titleId = useId()
  const descriptionId = useId()

  useEffect(() => {
    if (!open) return
    const closeOnEscape = (event: KeyboardEvent) => event.key === 'Escape' && onCancel()
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [open, onCancel])

  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-ink-950/80 p-4 transition-opacity duration-200 ease-out starting:opacity-0">
      <dialog
        open
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        className="static w-full max-w-md rounded-xl border border-ink-700 bg-ink-800 p-6 text-ink-200 shadow-2xl shadow-ink-950/70 transition-[opacity,transform] duration-200 ease-out starting:opacity-0 motion-safe:starting:scale-[0.96]"
      >
        <h2 id={titleId} className="font-display text-xl font-semibold text-ink-100">
          {title}
        </h2>
        {description && (
          <p id={descriptionId} className="mt-2 text-sm text-ink-400">
            {description}
          </p>
        )}
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel} autoFocus>
            Cancelar
          </Button>
          <Button variant="danger" loading={loading} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </dialog>
    </div>
  )
}
