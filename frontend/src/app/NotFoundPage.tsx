import { Link } from 'react-router-dom'

import { buttonClasses } from '@/shared/ui/buttonStyles'
import { EmptyState } from '@/shared/ui/EmptyState'

export function NotFoundPage() {
  return (
    <EmptyState
      title="Página não encontrada"
      description="O endereço acessado não existe."
      action={
        <Link to="/" className={buttonClasses('secondary')}>
          Voltar ao catálogo
        </Link>
      }
    />
  )
}
