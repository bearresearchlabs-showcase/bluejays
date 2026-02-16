/**
 * Integration tests: Login API error paths against running app
 * @jest-environment node
 *
 * Run: npm run dev:test (port 3007), then in another terminal:
 *   npm run test:integration
 */
import { BASE_URL, PASSWORD } from './config'

function skipIfAppNotRunning(e: unknown): void {
  if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
    console.warn('Skipping: app not running on ' + BASE_URL)
    return
  }
  throw e
}

describe('Integration: Login errors (app on ' + BASE_URL + ')', () => {
  it('POST /api/login with invalid credentials returns 307 to /login?err=...', async () => {
    try {
      const form = new URLSearchParams()
      form.set('user', 'annotator')
      form.set('password', 'wrong')
      const res = await fetch(BASE_URL + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.toString(),
        redirect: 'manual',
      })
      expect(res.status).toBe(307)
      const loc = res.headers.get('location') || ''
      expect(loc).toMatch(/\/login/)
      expect(loc).toMatch(/err=/)
      expect(loc).toMatch(/Invalid/)
    } catch (e) {
      skipIfAppNotRunning(e)
    }
  })

  it('POST /api/login with unknown user returns 307 to /login?err=...', async () => {
    try {
      const form = new URLSearchParams()
      form.set('user', 'nonexistent')
      form.set('password', PASSWORD)
      const res = await fetch(BASE_URL + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.toString(),
        redirect: 'manual',
      })
      expect(res.status).toBe(307)
      const loc = res.headers.get('location') || ''
      expect(loc).toMatch(/\/login/)
      expect(loc).toMatch(/err=/)
    } catch (e) {
      skipIfAppNotRunning(e)
    }
  })

  it('POST /api/login with empty body returns 307 to /login?err=...', async () => {
    try {
      const res = await fetch(BASE_URL + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: '',
        redirect: 'manual',
      })
      expect(res.status).toBe(307)
      const loc = res.headers.get('location') || ''
      expect(loc).toMatch(/\/login/)
      expect(loc).toMatch(/err=/)
    } catch (e) {
      skipIfAppNotRunning(e)
    }
  })

  it('POST /api/login with valid credentials returns 307 to / or /customer', async () => {
    try {
      const form = new URLSearchParams()
      form.set('user', 'annotator')
      form.set('password', PASSWORD)
      const res = await fetch(BASE_URL + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.toString(),
        redirect: 'manual',
      })
      expect(res.status).toBe(307)
      const loc = res.headers.get('location') || ''
      expect(loc).toMatch(/^(\/|https?:\/\/)/)
      expect(loc).not.toMatch(/err=/)
      expect(res.headers.get('set-cookie')).toMatch(/annotator_session/)
    } catch (e) {
      skipIfAppNotRunning(e)
    }
  })
})
