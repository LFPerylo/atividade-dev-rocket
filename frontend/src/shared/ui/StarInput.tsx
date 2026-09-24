import { formatStars, STAR_COUNT, STAR_VALUES, starFill } from '@/domain/rating'
import { StarIcon } from '@/shared/ui/StarIcon'
import { useId } from 'react'

type StarInputProps = {
  value: number | null
  onChange: (value: number) => void
  invalid?: boolean
  describedBy?: string
}

const HALF_STAR_SLOTS = [0.5, ...STAR_VALUES]

export function StarInput({ value, onChange, invalid = false, describedBy }: StarInputProps) {
  const name = useId()
  const displayed = value ?? 0

  return (
    <fieldset
      aria-invalid={invalid}
      aria-describedby={describedBy}
      className="flex items-center gap-3"
    >
      <legend className="sr-only">Nota em estrelas</legend>
      <div className="relative flex">
        {Array.from({ length: STAR_COUNT }, (_, index) => (
          <span key={index} className="relative size-9">
            <StarIcon className="absolute inset-0 text-ink-700" />
            <span
              className="absolute inset-0 overflow-hidden"
              style={{ width: `${starFill(displayed, index) * 100}%` }}
            >
              <StarIcon className="size-9 text-star-400" />
            </span>
          </span>
        ))}
        <div className="absolute inset-0 flex">
          {HALF_STAR_SLOTS.map((option) =>
            STAR_VALUES.includes(option) ? (
              <label
                key={option}
                className="h-full flex-1 cursor-pointer rounded-sm has-focus-visible:outline-2 has-focus-visible:outline-accent-400"
              >
                <input
                  type="radio"
                  name={name}
                  value={option}
                  checked={value === option}
                  onChange={() => onChange(option)}
                  aria-label={`${formatStars(option)} estrelas`}
                  className="sr-only"
                />
              </label>
            ) : (
              <span key={option} className="h-full flex-1" />
            ),
          )}
        </div>
      </div>
      <span className="min-w-8 text-sm font-semibold text-ink-100 tabular-nums">
        {value ? formatStars(value) : ''}
      </span>
    </fieldset>
  )
}
