import { expect, type Page, test } from '@playwright/test'

async function login(page: Page) {
  await page.goto('/login')
  await page.getByLabel('E-mail').fill('admin@rocketlab.dev')
  await page.getByLabel('Senha').fill('rocketlab2026')
  await page.getByRole('button', { name: 'Entrar' }).click()
  await expect(page.getByRole('button', { name: 'Sair' })).toBeVisible()
}

test('admin manages a movie and its reviews end to end', async ({ page }) => {
  const title = `Filme E2E ${Date.now()}`
  await login(page)

  await page.getByRole('link', { name: 'Adicionar filme' }).click()
  await page.getByLabel('Título').fill(title)
  await page.getByLabel('Diretores').fill('Diretora Teste')
  await page.getByText('Drama', { exact: true }).click()
  await page.getByLabel('Ano de lançamento').fill('2024')
  await page.getByLabel('Sinopse').fill('Uma história criada pelos testes.')
  await page.getByRole('button', { name: 'Cadastrar filme' }).click()

  await expect(page.getByRole('heading', { level: 1, name: title })).toBeVisible()
  await expect(page.getByText('Nenhuma avaliação')).toBeVisible()

  await page.getByRole('radio', { name: '4,5 estrelas' }).locator('..').click()
  await page.getByLabel('Resenha').fill('Excelente direção.')
  await page.getByRole('button', { name: 'Publicar avaliação' }).click()

  const summary = page.getByRole('region', { name: 'Média das avaliações' })
  await expect(summary.getByText('4,5')).toBeVisible()
  await expect(summary.getByText('1 avaliação')).toBeVisible()
  await expect(page.getByText('Excelente direção.')).toBeVisible()

  await page.getByRole('link', { name: 'Editar' }).click()
  await page.getByLabel('Título').fill(`${title} (editado)`)
  await page.getByRole('button', { name: 'Salvar alterações' }).click()
  await expect(page.getByRole('heading', { level: 1, name: `${title} (editado)` })).toBeVisible()

  await page.getByRole('button', { name: 'Remover' }).click()
  await page.getByRole('dialog').getByRole('button', { name: 'Remover filme' }).click()
  await expect(page).toHaveURL('/')

  await page.getByRole('searchbox', { name: 'Buscar filmes' }).fill(title)
  await expect(page.getByText('Nenhum filme encontrado')).toBeVisible()
})

test('login rejects wrong credentials', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('E-mail').fill('admin@rocketlab.dev')
  await page.getByLabel('Senha').fill('senha-errada')
  await page.getByRole('button', { name: 'Entrar' }).click()

  await expect(page.getByText('E-mail ou senha inválidos')).toBeVisible()
})
