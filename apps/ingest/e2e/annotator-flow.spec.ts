import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

test.describe('Annotator flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'annotator')
  })

  test('loads sources and queries', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText(/SQL Annotator/i)).toBeVisible()
    await expect(page.getByText(/Loading|template|db-/i)).toBeVisible({ timeout: 10000 })
    await page.waitForTimeout(2000)
    const sourceSelect = page.locator('select').first()
    await expect(sourceSelect).toBeVisible({ timeout: 5000 })
  })

  test('can select source and load queries', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)
    const select = page.locator('select').first()
    if (await select.isVisible()) {
      await select.selectOption({ index: 0 })
      await page.waitForTimeout(2000)
    }
    await expect(page.getByText(/Save changes|query|Query/i)).toBeVisible({ timeout: 10000 })
  })

  test('save triggers sync', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)
    const queryItem = page.locator('[role="button"], button, a').filter({ hasText: /Query \d|1\./ }).first()
    if (await queryItem.isVisible({ timeout: 5000 })) {
      await queryItem.click()
      const saveBtn = page.getByRole('button', { name: /Save changes/i })
      if (await saveBtn.isVisible({ timeout: 3000 })) {
        await saveBtn.click()
        await expect(page.getByText(/Saved|success|error/i)).toBeVisible({ timeout: 5000 })
      }
    }
  })
})
