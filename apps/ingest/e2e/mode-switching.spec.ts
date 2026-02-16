import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

/**
 * E2E: Staff mode switching (Annotator | Staff | Customer | System owner)
 * BDD: Staff can switch modes to preview different role views.
 */
test.describe('Mode switching', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'staff')
  })

  test('staff sees Mode selector with Annotator, Staff, Customer, System owner', async ({ page }) => {
    await page.goto('/')
    const modeSelect = page.getByTestId('role-select')
    await expect(modeSelect).toBeVisible({ timeout: 10000 })
    await expect(modeSelect).toContainText('Annotator')
    await expect(modeSelect).toContainText('Staff')
    await expect(modeSelect).toContainText('Customer')
    await expect(modeSelect).toContainText('System owner')
  })

  test('staff in Staff mode can access pipeline and customer portal', async ({ page }) => {
    await page.goto('/')
    await page.getByTestId('role-select').selectOption('staff')
    await page.waitForTimeout(500)
    await page.goto('/staff/pipeline')
    await expect(page.getByText(/Pipeline|Scale-style/i)).toBeVisible({ timeout: 10000 })
    await page.goto('/customer')
    await expect(page.getByText(/Customer Portal|Task overview|export/i)).toBeVisible({ timeout: 10000 })
  })

  test('staff in Customer mode sees customer views only', async ({ page }) => {
    await page.goto('/')
    await page.getByTestId('role-select').selectOption('customer')
    await page.waitForTimeout(500)
    await page.goto('/customer')
    await expect(page.getByText(/Customer Portal|Task overview|export/i)).toBeVisible({ timeout: 10000 })
    await page.goto('/staff/pipeline', { waitUntil: 'commit' })
    await page.waitForURL(/\/(?!staff\/pipeline)/, { timeout: 5000 })
    expect(page.url()).not.toContain('/staff/pipeline')
  })

  test('staff in System owner mode can access privileges', async ({ page }) => {
    await page.goto('/')
    await page.getByTestId('role-select').selectOption('system_owner')
    await page.waitForTimeout(500)
    await page.goto('/admin/privileges')
    await expect(page.getByText(/Privilege Configuration|Annotator|customer/i)).toBeVisible({ timeout: 10000 })
  })

  test('staff in Annotator mode cannot access customer or pipeline', async ({ page }) => {
    await page.goto('/')
    await page.getByTestId('role-select').selectOption('annotator')
    await page.waitForTimeout(500)
    await page.goto('/customer', { waitUntil: 'commit' })
    await page.waitForURL(/\/(?!customer)/, { timeout: 5000 })
    expect(page.url()).not.toContain('/customer')
  })
})
