import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

/**
 * E2E: New features from roadmap plan
 * - Schema view, ChartDB/Liam tools, LiveSQLBench ingest, interactive charts
 */
test.describe('New features', () => {
  test.describe('Schema view', () => {
    test('schema view or selector visible on dashboard', async ({ page }) => {
      await loginAs(page, 'staff')
      await page.goto('/dashboard')
      await expect(page.getByText(/Schema|Database/i)).toBeVisible({ timeout: 15000 })
    })

    test('schema view visible on customer portal', async ({ page }) => {
      await loginAs(page, 'customer')
      await page.goto('/customer')
      await expect(page.getByText(/Schema|Database|Tools/i)).toBeVisible({ timeout: 15000 })
    })
  })

  test.describe('ChartDB and Liam tools', () => {
    test('tools section with ChartDB or Liam link visible', async ({ page }) => {
      await loginAs(page, 'staff')
      await page.goto('/dashboard')
      await expect(page.getByRole('link', { name: /Open ChartDB|Open Liam ERD/i })).toBeVisible({ timeout: 15000 })
    })

    test('tools section visible on customer portal', async ({ page }) => {
      await loginAs(page, 'customer')
      await page.goto('/customer')
      await expect(page.getByText('Tools')).toBeVisible({ timeout: 15000 })
    })
  })

  test.describe('LiveSQLBench ingest', () => {
    test('staff sees LiveSQLBench ingest form on dashboard', async ({ page }) => {
      await loginAs(page, 'staff')
      await page.goto('/dashboard')
      await expect(page.getByText(/LiveSQLBench|Ingest/i)).toBeVisible({ timeout: 15000 })
    })

    test('staff can submit LiveSQLBench JSON', async ({ page }) => {
      await loginAs(page, 'staff')
      await page.goto('/dashboard')
      const textarea = page.locator('textarea').first()
      await expect(textarea).toBeVisible({ timeout: 15000 })
      await textarea.fill(JSON.stringify({
        instance_id: 'test_1',
        selected_database: 'alien',
        query: 'Show signals.',
        category: 'Query',
      }))
      await page.getByRole('button', { name: /Ingest/i }).click()
      await expect(page.getByTestId('livesqlbench-result')).toBeVisible({ timeout: 10000 })
    })
  })

  test.describe('Interactive charts (drill-down)', () => {
    test('customer sees click-to-filter hint on Task Status chart', async ({ page }) => {
      await loginAs(page, 'customer')
      await page.goto('/customer')
      await expect(page.getByText(/Task Status|click to filter/i)).toBeVisible({ timeout: 15000 })
    })

    test('clicking pie slice shows filter and clear button', async ({ page }) => {
      await loginAs(page, 'customer')
      await page.goto('/customer')
      await page.waitForTimeout(3000)
      const pie = page.locator('.recharts-pie-sector').first()
      await expect(pie).toBeVisible({ timeout: 10000 })
      await pie.click()
      await expect(page.getByText(/Filter:|Clear filter/i)).toBeVisible({ timeout: 5000 })
    })
  })
})
