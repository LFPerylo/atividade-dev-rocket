import { expect, test } from '@playwright/test'

test('visitor creates an account and reviews a movie', async ({ page }) => {
  const email = `avaliadora.${Date.now()}@exemplo.com`
  await page.goto('/?busca=oppenheimer')
  await page.getByRole('link', { name: /^Oppenheimer 2023/ }).click()
  await page.getByRole('link', { name: 'crie uma conta' }).click()

  await page.getByLabel('Nome').fill('Bia Lima')
  await page.getByLabel('E-mail').fill(email)
  await page.getByLabel('Senha', { exact: true }).fill('senha-da-bia')
  await page.getByLabel('Confirme a senha').fill('senha-da-bia')
  await page.getByRole('button', { name: 'Criar conta' }).click()

  await expect(page.getByRole('heading', { level: 1, name: 'Oppenheimer' })).toBeVisible()
  await expect(page.getByText('Avaliando como Bia Lima')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Editar' })).toHaveCount(0)

  await page.getByRole('radio', { name: '4,0 estrelas' }).locator('..').click()
  await page.getByLabel('Resenha').fill('Som e montagem impressionantes.')
  await page.getByRole('button', { name: 'Publicar avaliação' }).click()

  await expect(page.getByText('Som e montagem impressionantes.')).toBeVisible()
  await expect(page.getByRole('list', { name: 'Avaliações' }).getByText('Bia Lima')).toBeVisible()
})

test('reviewers cannot open admin pages', async ({ page }) => {
  await page.goto('/cadastro')
  await page.getByLabel('Nome').fill('Caio Prado')
  await page.getByLabel('E-mail').fill(`caio.${Date.now()}@exemplo.com`)
  await page.getByLabel('Senha', { exact: true }).fill('senha-do-caio')
  await page.getByLabel('Confirme a senha').fill('senha-do-caio')
  await page.getByRole('button', { name: 'Criar conta' }).click()
  await expect(page.getByRole('button', { name: 'Sair' })).toBeVisible()

  await page.goto('/filmes/novo')

  await expect(page.getByText('Acesso restrito a administradores')).toBeVisible()
})
