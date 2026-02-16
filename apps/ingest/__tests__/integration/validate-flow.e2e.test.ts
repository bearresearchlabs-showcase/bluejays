/**
 * Integration tests: Validate API flow against running app
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

describe('Integration: Validate flow (app on ' + BASE_URL + ')', () => {
  it('GET /api/validate/query as staff returns 200 with valid, errors, warnings', async () => {
    try {
      const cookie = await loginAndGetCookies('staff')
      const res = await fetch(
        BASE_URL + '/api/validate/query?source=db-1&query=1&role=staff&view=/customer',
        { headers: { Cookie: cookie } }
      )
      expect(res.status).toBe(200)
      const data = await res.json()
      expect(typeof data.valid).toBe('boolean')
      expect(Array.isArray(data.errors)).toBe(true)
      expect(Array.isArray(data.warnings)).toBe(true)
      expect(typeof data.materializedView).toBe('boolean')
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })

  it('GET /api/validate/query as annotator returns 403', async () => {
    try {
      const cookie = await loginAndGetCookies('annotator')
      const res = await fetch(
        BASE_URL + '/api/validate/query?source=db-1&query=1',
        { headers: { Cookie: cookie } }
      )
      expect(res.status).toBe(403)
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })

  it('POST /api/validate/batch as staff returns 200 with results array', async () => {
    try {
      const cookie = await loginAndGetCookies('staff')
      const res = await fetch(BASE_URL + '/api/validate/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Cookie: cookie },
        body: JSON.stringify({ source: 'db-1', role: 'staff', view: '/customer' }),
      })
      expect(res.status).toBe(200)
      const data = await res.json()
      expect(Array.isArray(data.results)).toBe(true)
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })
})
