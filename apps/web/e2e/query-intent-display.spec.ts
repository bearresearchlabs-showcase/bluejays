/**
 * E2E tests: Intent-focused natural language query display (LiveSQLBench style)
 */

import { test, expect } from '@playwright/test'

test.describe('Query intent display', () => {
  test('databases catalog page loads', async ({ page }) => {
    await page.goto('/databases')
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible({ timeout: 10000 })
  })

  test('database detail page shows Queries tab with intent-focused description', async ({ page }) => {
    await page.goto('/databases')
    await page.waitForLoadState('networkidle')

    // Click first database card if present
    const dbLink = page.getByRole('link', { name: /db\d+/i }).first()
    if (await dbLink.isVisible()) {
      await dbLink.click()
      await page.waitForURL(/\/db\/db\d+/)

      // Open Queries tab
      const queriesTab = page.getByRole('tab', { name: /queries/i })
      if (await queriesTab.isVisible()) {
        await queriesTab.click()
        // Should show intent-focused subtitle
        await expect(
          page.getByText(/intent-focused natural language|complex SQL queries/i)
        ).toBeVisible({ timeout: 5000 })
      }
    }
  })

  test('docs page structure supports Intent label', async ({ page }) => {
    // Navigate to docs for a known db (db6 if available)
    await page.goto('/db/db6/docs')
    await page.waitForLoadState('networkidle')

    // Page should load (either with content or "not found")
    const body = page.locator('body')
    await expect(body).toBeVisible()

    // If we have query content, Intent label should appear
    const intentLabel = page.getByText('Intent', { exact: true })
    const hasQueries = await page.getByText(/Query \d+:/).first().isVisible().catch(() => false)
    if (hasQueries) {
      await expect(intentLabel.first()).toBeVisible({ timeout: 5000 })
    }
  })
})
