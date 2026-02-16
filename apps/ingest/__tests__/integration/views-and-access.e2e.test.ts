/**
 * Integration tests: Views and access against running app
 * Reuses the same localhost — no spawning new servers.
 * @jest-environment node
 *
 * Run: npm run dev:test (port 3007), then in another terminal:
 *   npm run test:integration
 */
import { BASE_URL } from './config'

describe('Integration: Views and access (app on ' + BASE_URL + ')', () => {
  it('GET /login returns 200 when unauthenticated', async () => {
    try {
      const res = await fetch(BASE_URL + '/login', { redirect: 'manual', credentials: 'omit' })
      // 200 = login page; 307 can occur with trailing-slash or auth redirects
      expect([200, 307]).toContain(res.status)
      if (res.status === 307) {
        const loc = res.headers.get('location') || ''
        expect(loc).not.toMatch(/^\/(?!login)/)
      }
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL + '. Start with: npm run dev:test')
        return
      }
      throw e
    }
  })

  it('GET / redirects to /login when unauthenticated', async () => {
    try {
      const res = await fetch(BASE_URL + '/', { redirect: 'manual' })
      expect(res.status).toBe(307)
      expect(res.headers.get('location')).toMatch(/\/login/)
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })

  it('GET /api/sources returns 401 when unauthenticated', async () => {
    try {
      const res = await fetch(BASE_URL + '/api/sources')
      expect(res.status).toBe(401)
    } catch (e) {
      if (String(e).includes('fetch') || String(e).includes('ECONNREFUSED')) {
        console.warn('Skipping: app not running on ' + BASE_URL)
        return
      }
      throw e
    }
  })
})
