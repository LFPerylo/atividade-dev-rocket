import { clsx } from 'clsx'
import type { ButtonHTMLAttributes } from 'react'

import { buttonClasses, type ButtonVariant } from '@/shared/ui/buttonStyles'
import { Spinner } from '@/shared/ui/Spinner'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant
  loading?: boolean
}

export function Button({
  variant = 'primary',
  loading = false,
  disabled,
  className,
  children,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading}
      className={clsx(buttonClasses(variant), className)}
      {...props}
    >
      {loading && <Spinner />}
      {children}
    </button>
  )
}
