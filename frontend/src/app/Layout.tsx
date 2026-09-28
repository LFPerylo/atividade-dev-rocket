import { Link, NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '@/features/auth/authContext'
import { Button } from '@/shared/ui/Button'
import { buttonClasses } from '@/shared/ui/buttonStyles'

function Logo() {
  return (
    <Link to="/" aria-label="Claquete — início" className="flex items-center gap-2">
      <svg viewBox="0 0 32 32" aria-hidden="true" className="size-8">
        <rect width="32" height="32" rx="7" fill="#1c2228" />
        <path d="M6 13h20v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z" fill="#00e054" />
        <path d="m6 9 19-4 1 4-19 4z" fill="#ffb020" />
      </svg>
      <span className="font-display text-2xl font-semibold tracking-tight text-ink-100">
        Claquete
      </span>
    </Link>
  )
}

export function Layout() {
  const { status, user, logout } = useAuth()

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-40 border-b border-ink-800 bg-ink-900/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
          <Logo />
          <nav className="flex items-center gap-2 text-sm">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                isActive
                  ? 'px-3 py-2 font-semibold text-ink-100'
                  : 'px-3 py-2 text-ink-400 hover:text-ink-100'
              }
            >
              Filmes
            </NavLink>
            {status === 'authenticated' ? (
              <>
                <span className="hidden text-ink-400 sm:inline">{user?.nome}</span>
                <Button variant="ghost" onClick={logout}>
                  Sair
                </Button>
              </>
            ) : (
              <>
                <Link to="/login" className="px-3 py-2 text-ink-400 hover:text-ink-100">
                  Entrar
                </Link>
                <Link to="/cadastro" className={buttonClasses('primary')}>
                  Criar conta
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">
        <Outlet />
      </main>
      <footer className="border-t border-ink-800 py-6 text-center text-xs text-ink-600">
        Claquete · RocketLab 2026 · Dados de filmes fornecidos pelo TMDB
      </footer>
    </div>
  )
}
