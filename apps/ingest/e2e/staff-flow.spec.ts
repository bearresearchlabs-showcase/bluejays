import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

test.describe('Staff flow', () => {
  test('staff can access /staff/pipeline', async ({ page }) => {
    await loginAs(page, 'staff')
    await page.goto('/staff/pipeline')
    await expect(page.getByText(/Pipeline|Scale-style/i)).toBeVisible({ timeout: 10000 })
  })

  test('staff sees pipeline phases', async ({ page }) => {
    await loginAs(page, 'staff')
    await page.goto('/staff/pipeline')
    await expect(page.getByText(/Attempt|Review|Complete|Rejected/i)).toBeVisible({ timeout: 10000 })
  })

  test('annotator redirected from /staff/pipeline', async ({ page }) => {
    await loginAs(page, 'annotator')
    await page.goto('/staff/pipeline', { waitUntil: 'commit' })
    await page.waitForURL(/\/(?!staff\/pipeline)/, { timeout: 5000 })
    expect(page.url()).not.toContain('/staff/pipeline')
  })
})
