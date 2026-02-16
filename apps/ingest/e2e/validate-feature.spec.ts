import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

/**
 * E2E: Query validation feature
 * BDD: Staff validates queries per role/view; side panel shows results and MV status.
 */
test.describe('Validate feature', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'staff')
    await page.getByTestId('role-select').selectOption('staff').catch(() => {})
    await page.waitForTimeout(300)
  })

  test('staff can navigate to /validate', async ({ page }) => {
    await page.goto('/validate')
    await expect(page.getByText(/Query Validation|Validate SQL per role/i)).toBeVisible({ timeout: 10000 })
  })

  test('validate page shows database, role, view selectors', async ({ page }) => {
    await page.goto('/validate')
    await expect(page.getByText(/Database|Role|View/i)).toBeVisible({ timeout: 10000 })
  })

  test('validate page shows query list when database selected', async ({ page }) => {
    await page.goto('/validate')
    await page.waitForTimeout(1000)
    await expect(page.getByText(/Queries|Query \d/i).first()).toBeVisible({ timeout: 15000 })
  })

  test('clicking a query loads validation in side panel', async ({ page }) => {
    await page.goto('/validate')
    await page.waitForTimeout(1500)
    const queryButton = page.getByRole('button', { name: /Query 1/i }).first()
    await queryButton.click({ timeout: 10000 })
    await page.waitForTimeout(500)
    await expect(page.getByText(/Pass|Fail|Validation/i)).toBeVisible({ timeout: 5000 })
  })

  test('side panel shows Validation when no query selected', async ({ page }) => {
    await page.goto('/validate')
    await expect(page.getByText(/Select a query to see validation details/i)).toBeVisible({ timeout: 10000 })
  })
})
