import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

test.describe('Login flow', () => {
  test('GET / redirects to /login when unauthenticated', async ({ page }) => {
    await page.goto('/', { waitUntil: 'commit' })
    await page.waitForURL(/\/login/)
    expect(page.url()).toContain('/login')
  })

  test('GET /login returns 200 and shows login form', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByRole('heading', { name: /SQL Annotator/i })).toBeVisible()
    await expect(page.getByLabel(/username/i)).toBeVisible()
    await expect(page.getByLabel(/password/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /log in/i })).toBeVisible()
  })

  test('invalid credentials show error', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/username/i).fill('annotator')
    await page.getByLabel(/password/i).fill('wrong')
    await page.getByRole('button', { name: /log in/i }).click()
    await expect(page.getByText(/invalid|error/i)).toBeVisible({ timeout: 5000 })
    expect(page.url()).toContain('/login')
  })

  test('valid staff redirects to /', async ({ page }) => {
    await loginAs(page, 'staff')
    expect(page.url()).not.toContain('/login')
    await expect(page.getByText(/SQL Annotator/i)).toBeVisible()
  })

  test('valid annotator redirects to /', async ({ page }) => {
    await loginAs(page, 'annotator')
    expect(page.url()).not.toContain('/login')
    await expect(page.getByText(/SQL Annotator/i)).toBeVisible()
  })

  test('valid customer redirects to /customer', async ({ page }) => {
    await loginAs(page, 'customer')
    expect(page.url()).toContain('/customer')
    await expect(page.getByText(/Select database|Customer/i)).toBeVisible()
  })
})
