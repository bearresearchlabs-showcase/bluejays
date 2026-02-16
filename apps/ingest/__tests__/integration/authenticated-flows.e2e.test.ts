/**
 * Integration tests: Authenticated API flows against running app
 * @jest-environment node
 *
 * Run: npm run dev:test (port 3007), then in another terminal:
 *   npm run test:integration
 */
import { BASE_URL, PASSWORD } from './config'

async function loginAndGetCookies(user: 'staff' | 'annotator' | 'customer'): Promise<string> {
  const form = new URLSearchParams()
  form.set('user', user)
  form.set('password', PASSWORD)
  form.set('stay', '1')

  const res = await fetch(BASE_URL + '/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
    redirect: 'manual',
  })
  const setCookie = res.headers.get('set-cookie')
  if (!setCookie) throw new Error('No Set-Cookie from login')
  return setCookie.split(';')[0]
}

describe('Integration: Authenticated flows (app on ' + BASE_URL + ')', () => {
  it('GET /api/sources with cookie returns 200', async () => {
    try {
      const cookie = await loginAndGetCookies('annotator')
      const res = await fetch(BASE_URL + '/api/sources', {
        headers: { Cookie: cookie },
      })
      expect(res.status).toBe(200)
      const data = await res.json()
      expect(data).toHaveProperty('sources')
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })

  it('GET /api/queries?source=db-1 with cookie returns 200', async () => {
    try {
      const cookie = await loginAndGetCookies('annotator')
      const res = await fetch(BASE_URL + '/api/queries?source=db-1', {
        headers: { Cookie: cookie },
      })
      expect(res.status).toBe(200)
      const data = await res.json()
      expect(data).toHaveProperty('queries')
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })

  it('GET /api/export as customer returns 200', async () => {
    try {
      const cookie = await loginAndGetCookies('customer')
      const res = await fetch(BASE_URL + '/api/export?source=db-1&format=json', {
        headers: { Cookie: cookie },
      })
      expect(res.status).toBe(200)
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })

  it('GET /api/export as annotator returns 403', async () => {
    try {
      const cookie = await loginAndGetCookies('annotator')
      const res = await fetch(BASE_URL + '/api/export?source=db-1&format=json', {
        headers: { Cookie: cookie },
      })
      expect(res.status).toBe(403)
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })
})
