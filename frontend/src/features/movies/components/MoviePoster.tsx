import { clsx } from 'clsx'
import { useState } from 'react'

type MoviePosterProps = {
  title: string
  url: string | null
  className?: string
}

export function MoviePoster({ title, url, className }: MoviePosterProps) {
  const [failed, setFailed] = useState(false)
  const showImage = url && !failed
  return (
    <div
      className={clsx(
        'relative aspect-[2/3] overflow-hidden rounded-md bg-ink-800 ring-1 ring-ink-700',
        className,
      )}
    >
      {showImage ? (
        <img
          src={url}
          alt=""
          loading="lazy"
          onError={() => setFailed(true)}
          className="size-full object-cover"
        />
      ) : (
        <div className="grid size-full place-items-center bg-gradient-to-br from-ink-700 to-ink-900 p-3 text-center">
          <span className="font-display text-sm text-ink-400">{title}</span>
        </div>
      )}
    </div>
  )
}
