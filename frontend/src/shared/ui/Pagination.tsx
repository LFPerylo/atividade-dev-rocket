import { Button } from '@/shared/ui/Button'

type PaginationProps = {
  page: number
  pages: number
  onChange: (page: number) => void
}

export function Pagination({ page, pages, onChange }: PaginationProps) {
  if (pages < 1) return null
  return (
    <nav aria-label="Paginação" className="flex items-center justify-center gap-4">
      <Button
        variant="secondary"
        aria-label="Página anterior"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
      >
        ←
      </Button>
      <span className="text-sm text-ink-400 tabular-nums">
        Página {page} de {pages}
      </span>
      <Button
        variant="secondary"
        aria-label="Próxima página"
        disabled={page >= pages}
        onClick={() => onChange(page + 1)}
      >
        →
      </Button>
    </nav>
  )
}
