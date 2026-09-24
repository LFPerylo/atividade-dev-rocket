import { createBrowserRouter, Outlet } from 'react-router-dom'

import { Layout } from '@/app/Layout'
import { NotFoundPage } from '@/app/NotFoundPage'
import { RequireAuth } from '@/features/auth/RequireAuth'
import { CatalogPage } from '@/features/movies/pages/CatalogPage'

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { index: true, element: <CatalogPage /> },
      {
        path: 'login',
        lazy: () =>
          import('@/features/auth/LoginPage').then(({ LoginPage }) => ({ Component: LoginPage })),
      },
      {
        path: 'filmes/:id',
        lazy: () =>
          import('@/features/movies/pages/MovieDetailsPage').then(({ MovieDetailsPage }) => ({
            Component: MovieDetailsPage,
          })),
      },
      {
        element: (
          <RequireAuth>
            <Outlet />
          </RequireAuth>
        ),
        children: [
          {
            path: 'filmes/novo',
            lazy: () =>
              import('@/features/movies/pages/MovieCreatePage').then(({ MovieCreatePage }) => ({
                Component: MovieCreatePage,
              })),
          },
          {
            path: 'filmes/:id/editar',
            lazy: () =>
              import('@/features/movies/pages/MovieEditPage').then(({ MovieEditPage }) => ({
                Component: MovieEditPage,
              })),
          },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
