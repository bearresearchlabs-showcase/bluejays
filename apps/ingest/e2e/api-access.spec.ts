import { test, expect } from '@playwright/test'
import { loginAs } from './fixtures/auth'

test.describe('API access by role', () => {
  test('unauthenticated GET /api/sources returns 401', async ({ request }) => {
    const res = await request.get('/api/sources')
    expect(res.status()).toBe(401)
  })

  test('unauthenticated GET /api/queries returns 401', async ({ request }) => {
    const res = await request.get('/api/queries?source=db-1')
    expect(res.status()).toBe(401)
  })

  test('customer GET /api/export returns 200', async ({ page }) => {
    await loginAs(page, 'customer')
    const res = await page.request.get('/api/export?source=db-1&format=json')
    expect(res.status()).toBe(200)
  })

  test('annotator GET /api/export returns 403', async ({ page }) => {
    await loginAs(page, 'annotator')
    const res = await page.request.get('/api/export?source=db-1&format=json')
    expect(res.status()).toBe(403)
  })
})
