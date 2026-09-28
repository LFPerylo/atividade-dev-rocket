import { MagnifyingGlassIcon } from '@phosphor-icons/react'
import { useState } from 'react'

import { useDebouncedCallback } from '@/shared/hooks/useDebouncedCallback'

const SEARCH_DELAY_MS = 300

type SearchBarProps = {
  initialValue: string
  onSearch: (term: string) => void
}

export function SearchBar({ initialValue, onSearch }: SearchBarProps) {
  const [term, setTerm] = useState(initialValue)
  const [syncedValue, setSyncedValue] = useState(initialValue)
  const [emittedValue, setEmittedValue] = useState(initialValue)
  const debouncedSearch = useDebouncedCallback((value: string) => {
    setEmittedValue(value)
    onSearch(value)
  }, SEARCH_DELAY_MS)

  if (initialValue !== syncedValue) {
    setSyncedValue(initialValue)
    if (initialValue !== emittedValue) setTerm(initialValue)
  }

  return (
    <div className="relative">
      <MagnifyingGlassIcon
        aria-hidden="true"
        weight="bold"
        className="pointer-events-none absolute top-1/2 left-4 size-5 -translate-y-1/2 text-ink-400"
      />
      <input
        type="search"
        aria-label="Buscar filmes"
        placeholder="Buscar por título ou diretor"
        value={term}
        onChange={(event) => {
          setTerm(event.target.value)
          debouncedSearch(event.target.value)
        }}
        className="w-full rounded-full border border-ink-700 bg-ink-950 py-3 pr-4 pl-12 text-base text-ink-100 transition-colors placeholder:text-ink-500 focus:border-accent-400 focus:outline-none"
      />
    </div>
  )
}
