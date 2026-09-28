import { clsx } from 'clsx'
import type {
  InputHTMLAttributes,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from 'react'

const controlClasses = (invalid: boolean) =>
  clsx(
    'w-full rounded-md border bg-ink-950 px-3 py-2 text-sm text-ink-100 placeholder:text-ink-500',
    'transition-colors focus:border-accent-400 focus:outline-none',
    invalid ? 'border-danger-400' : 'border-ink-700',
  )

type FieldProps = {
  id: string
  label: string
  error?: string
  hint?: string
  children: ReactNode
}

export function Field({ id, label, error, hint, children }: FieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium text-ink-200">
        {label}
      </label>
      {children}
      {hint && !error && <p className="text-xs text-ink-500">{hint}</p>}
      {error && (
        <p id={`${id}-error`} role="alert" className="text-xs text-danger-400">
          {error}
        </p>
      )}
    </div>
  )
}

type InvalidProp = { invalid?: boolean }

export function Input({
  invalid = false,
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & InvalidProp) {
  return (
    <input aria-invalid={invalid} className={clsx(controlClasses(invalid), className)} {...props} />
  )
}

export function TextArea({
  invalid = false,
  className,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & InvalidProp) {
  return (
    <textarea
      aria-invalid={invalid}
      className={clsx(controlClasses(invalid), className)}
      {...props}
    />
  )
}

export function Select({
  invalid = false,
  className,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & InvalidProp) {
  return (
    <select
      aria-invalid={invalid}
      className={clsx(controlClasses(invalid), className)}
      {...props}
    />
  )
}
