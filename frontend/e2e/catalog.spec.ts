import { expect, test } from '@playwright/test'

test('visitor searches the catalog and opens a movie', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText(/^\d{2}\.\d{3} filmes$/)).toBeVisible()

  await page.getByRole('searchbox', { name: 'Buscar filmes' }).fill('oppenheimer')
  await expect(page).toHaveURL(/busca=oppenheimer/)
  await page.getByRole('link', { name: /^Oppenheimer 2023/ }).click()

  await expect(page.getByRole('heading', { level: 1, name: 'Oppenheimer' })).toBeVisible()
  await expect(page.getByText('Christopher Nolan').first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'crie uma conta' })).toBeVisible()
})

test('visitor filters by genre and sorts by title', async ({ page }) => {
  await page.goto('/')

  await page.getByLabel('Gênero').selectOption({ label: 'Western' })
  await page.getByLabel('Ordenar por').selectOption('titulo')

  await expect(page).toHaveURL(/genero=.+&ordenar=titulo/)
  await expect(page.getByRole('link', { name: /Western|.+/ }).first()).toBeVisible()
})

test('protected pages redirect to login', async ({ page }) => {
  await page.goto('/filmes/novo')

  await expect(page).toHaveURL(/\/login\?next=%2Ffilmes%2Fnovo/)
  await expect(page.getByRole('heading', { name: 'Entrar' })).toBeVisible()
})
