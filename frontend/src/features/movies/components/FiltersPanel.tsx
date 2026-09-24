import type { CatalogFilters, SortField } from '@/domain/filters'
import { STAR_VALUES, formatStars } from '@/domain/rating'
import { useGenres } from '@/features/movies/api'
import { Button } from '@/shared/ui/Button'
import { Field, Input, Select } from '@/shared/ui/Field'

type FiltersPanelProps = {
  filters: CatalogFilters
  onChange: (changes: Partial<CatalogFilters>) => void
}

const SORT_LABELS: Record<SortField, string> = {
  popularidade: 'Popularidade',
  media: 'Média das avaliações',
  titulo: 'Título',
  ano: 'Ano de lançamento',
}

const toYear = (value: string) => (value ? Number(value) : null)

export function FiltersPanel({ filters, onChange }: FiltersPanelProps) {
  const { data: genres = [] } = useGenres()

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-6">
      <Field id="filtro-genero" label="Gênero">
        <Select
          id="filtro-genero"
          value={filters.genero}
          onChange={(event) => onChange({ genero: event.target.value })}
        >
          <option value="">Todos</option>
          {genres.map((genre) => (
            <option key={genre.id} value={genre.id}>
              {genre.nome}
            </option>
          ))}
        </Select>
      </Field>
      <Field id="filtro-ano-de" label="Ano de">
        <Input
          id="filtro-ano-de"
          type="number"
          inputMode="numeric"
          placeholder="1900"
          defaultValue={filters.anoDe ?? ''}
          onBlur={(event) => onChange({ anoDe: toYear(event.target.value) })}
        />
      </Field>
      <Field id="filtro-ano-ate" label="Ano até">
        <Input
          id="filtro-ano-ate"
          type="number"
          inputMode="numeric"
          placeholder="2030"
          defaultValue={filters.anoAte ?? ''}
          onBlur={(event) => onChange({ anoAte: toYear(event.target.value) })}
        />
      </Field>
      <Field id="filtro-estrelas" label="Nota mínima">
        <Select
          id="filtro-estrelas"
          value={filters.estrelasMin ?? ''}
          onChange={(event) =>
            onChange({ estrelasMin: event.target.value ? Number(event.target.value) : null })
          }
        >
          <option value="">Qualquer</option>
          {STAR_VALUES.map((value) => (
            <option key={value} value={value}>
              {formatStars(value)}★ ou mais
            </option>
          ))}
        </Select>
      </Field>
      <Field id="filtro-ordenar" label="Ordenar por">
        <Select
          id="filtro-ordenar"
          value={filters.ordenar}
          onChange={(event) => onChange({ ordenar: event.target.value as SortField })}
        >
          {Object.entries(SORT_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </Select>
      </Field>
      <div className="flex items-end">
        <Button
          variant="secondary"
          className="w-full"
          onClick={() => onChange({ ordem: filters.ordem === 'asc' ? 'desc' : 'asc' })}
        >
          {filters.ordem === 'asc' ? '↑ Crescente' : '↓ Decrescente'}
        </Button>
      </div>
    </div>
  )
}
