import { Page } from '@playwright/test'

const PASSWORD = process.env.TEST_PASSWORD || '123123'

export type UserRole = 'staff' | 'annotator' | 'customer'

export async function loginAs(page: Page, user: UserRole): Promise<void> {
  await page.goto('/login')
  await page.getByLabel(/username/i).fill(user)
  await page.getByLabel(/password/i).fill(PASSWORD)
  await page.getByRole('button', { name: /log in/i }).click()
  if (user === 'customer') {
    await page.waitForURL(/\/customer/)
  } else {
    await page.waitForURL(/\/(?!login)/)
  }
}
