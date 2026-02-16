import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

test.describe('Customer flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'customer')
  })

  test('customer portal loads', async ({ page }) => {
    await page.goto('/customer')
    await expect(page.getByText(/Select database|Customer/i)).toBeVisible()
  })

  test('tasks table and export links visible', async ({ page }) => {
    await page.goto('/customer')
    await page.waitForTimeout(3000)
    await expect(page.getByText(/Export CSV|Export JSON/i)).toBeVisible({ timeout: 10000 })
  })

  test('export CSV link has correct href', async ({ page }) => {
    await page.goto('/customer')
    await page.waitForTimeout(2000)
    const csvLink = page.getByRole('link', { name: /Export CSV/i })
    await expect(csvLink).toBeVisible({ timeout: 5000 })
    await expect(csvLink).toHaveAttribute('href', /\/api\/export.*format=csv/)
  })

  test('charts visible when tasks loaded', async ({ page }) => {
    await page.goto('/customer')
    await page.waitForTimeout(4000)
    const taskStatus = page.getByText('Task Status')
    const auditStatus = page.getByText('Audit Status')
    const completion = page.getByText('Completion')
    await expect(taskStatus.or(auditStatus).or(completion)).toBeVisible({ timeout: 5000 })
  })
})
