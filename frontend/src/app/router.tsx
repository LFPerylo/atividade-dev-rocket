import { createBrowserRouter, Outlet } from 'react-router-dom'

import { Layout } from '@/app/Layout'
import { NotFoundPage } from '@/app/NotFoundPage'
import { PageLoading } from '@/app/PageLoading'
import { RequireAdmin } from '@/features/auth/RequireAdmin'
import { CatalogPage } from '@/features/movies/pages/CatalogPage'

export const router = createBrowserRouter([
  {
    element: <Layout />,
    hydrateFallbackElement: <PageLoading />,
    children: [
      { index: true, element: <CatalogPage /> },
      {
        path: 'login',
        lazy: () =>
          import('@/features/auth/LoginPage').then(({ LoginPage }) => ({ Component: LoginPage })),
      },
      {
        path: 'cadastro',
        lazy: () =>
          import('@/features/auth/RegisterPage').then(({ RegisterPage }) => ({
            Component: RegisterPage,
          })),
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
          <RequireAdmin>
            <Outlet />
          </RequireAdmin>
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
