import type { ReactNode } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'

import { useAuth } from '@/features/auth/authContext'
import { buttonClasses } from '@/shared/ui/buttonStyles'
import { EmptyState } from '@/shared/ui/EmptyState'
import { Spinner } from '@/shared/ui/Spinner'

export function RequireAdmin({ children }: { children: ReactNode }) {
  const { status, isAdmin } = useAuth()
  const location = useLocation()

  if (status === 'loading') {
    return (
      <div className="grid place-items-center py-24 text-ink-400">
        <Spinner />
      </div>
    )
  }
  if (status === 'anonymous') {
    const next = encodeURIComponent(`${location.pathname}${location.search}`)
    return <Navigate to={`/login?next=${next}`} replace />
  }
  if (!isAdmin) {
    return (
      <EmptyState
        title="Acesso restrito a administradores"
        description="Sua conta pode avaliar filmes, mas só administradores gerenciam o catálogo."
        action={
          <Link to="/" className={buttonClasses('secondary')}>
            Voltar ao catálogo
          </Link>
        }
      />
    )
  }
  return children
}
