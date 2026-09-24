import { useState } from 'react'

import { useDebouncedCallback } from '@/shared/hooks/useDebouncedCallback'

const SEARCH_DELAY_MS = 300

type SearchBarProps = {
  initialValue: string
  onSearch: (term: string) => void
}

export function SearchBar({ initialValue, onSearch }: SearchBarProps) {
  const [term, setTerm] = useState(initialValue)
  const debouncedSearch = useDebouncedCallback(onSearch, SEARCH_DELAY_MS)

  return (
    <div className="relative">
      <svg
        aria-hidden="true"
        viewBox="0 0 24 24"
        className="pointer-events-none absolute top-1/2 left-4 size-5 -translate-y-1/2 text-ink-400"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.5-3.5" />
      </svg>
      <input
        type="search"
        aria-label="Buscar filmes"
        placeholder="Buscar por título ou diretor…"
        value={term}
        onChange={(event) => {
          setTerm(event.target.value)
          debouncedSearch(event.target.value)
        }}
        className="w-full rounded-full border border-ink-700 bg-ink-950 py-3 pr-4 pl-12 text-base text-ink-100 placeholder:text-ink-600 focus:border-accent-400 focus:outline-none"
      />
    </div>
  )
}
