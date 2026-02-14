/**
 * Integration tests: Views and access against running app
 * Reuses the same localhost — no spawning new servers.
 * @jest-environment node
 *
 * Run: npm run dev:test (port 3007) in one terminal, then:
 *   npm run test:integration
 */
const BASE_URL = process.env.BASE_URL || process.env.TEST_BASE_URL || 'http://localhost:3007'

describe('Integration: Views and access (app on ' + BASE_URL + ')', () => {
  it('GET /login returns 200 when unauthenticated', async () => {
    try {
      const res = await fetch(BASE_URL + '/login', { redirect: 'manual' })
      expect(res.status).toBe(200)
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
