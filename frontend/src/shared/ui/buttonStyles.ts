import { clsx } from 'clsx'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

const VARIANTS: Record<ButtonVariant, string> = {
  primary: 'bg-accent-500 text-ink-950 hover:bg-accent-400',
  secondary: 'bg-ink-700 text-ink-100 hover:bg-ink-600',
  ghost: 'bg-transparent text-ink-200 hover:bg-ink-800 hover:text-ink-100',
  danger: 'bg-danger-500 text-white hover:bg-danger-400',
}

export const buttonClasses = (variant: ButtonVariant = 'primary') =>
  clsx(
    'inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-semibold',
    'transition-colors disabled:cursor-not-allowed disabled:opacity-50',
    VARIANTS[variant],
  )
