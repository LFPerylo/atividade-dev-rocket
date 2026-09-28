import type { ReactNode } from 'react'

import { DEFAULT_FILTERS } from '@/domain/filters'
import { useMovies } from '@/features/movies/api'

const MOSAIC_SIZE = 9
const STAGGER_MS = 60

type AuthLayoutProps = {
  title: string
  description: string
  footer: ReactNode
  children: ReactNode
}

function PosterMosaic() {
  const { data } = useMovies(DEFAULT_FILTERS)
  const posters = (data?.itens ?? []).filter((movie) => movie.url_poster).slice(0, MOSAIC_SIZE)

  return (
    <div aria-hidden="true" className="relative hidden overflow-hidden rounded-2xl lg:block">
      <div className="grid -rotate-3 grid-cols-3 gap-3 p-2">
        {posters.map((movie, index) => (
          <img
            key={movie.id}
            src={movie.url_poster ?? ''}
            alt=""
            className="aspect-[2/3] w-full rounded-md object-cover ring-1 ring-ink-700 motion-safe:animate-poster-in"
            style={{ animationDelay: `${index * STAGGER_MS}ms` }}
          />
        ))}
      </div>
      <div className="absolute inset-0 bg-gradient-to-r from-ink-900 via-ink-900/40 to-transparent" />
    </div>
  )
}

export function AuthLayout({ title, description, footer, children }: AuthLayoutProps) {
  return (
    <section className="grid items-center gap-12 py-8 lg:grid-cols-[minmax(0,26rem)_1fr] lg:py-12">
      <div className="flex w-full max-w-md flex-col gap-6 justify-self-center lg:justify-self-start">
        <header>
          <h1 className="font-display text-3xl font-semibold text-ink-100">{title}</h1>
          <p className="mt-2 text-ink-400">{description}</p>
        </header>
        {children}
        <p className="text-sm text-ink-400">{footer}</p>
      </div>
      <PosterMosaic />
    </section>
  )
}
