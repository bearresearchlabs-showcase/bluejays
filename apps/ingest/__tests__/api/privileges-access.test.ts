/**
 * API: Privileges config access
 * Only staff in admin mode can POST (configure) privileges.
 * @jest-environment node
 */
jest.mock('@/lib/auth', () => ({
  getSession: jest.fn(),
  getActiveRole: jest.fn(),
}))

jest.mock('@/lib/privileges', () => {
  const actual = jest.requireActual('@/lib/privileges')
  return {
    ...actual,
    savePrivilegesConfig: jest.fn(),
  }
})

const authPriv = require('@/lib/auth')
const privilegesRoute = require('@/app/api/privileges/route')

describe('API /api/privileges GET', () => {
  it('returns views for annotator', async () => {
    ;(authPriv.getSession as jest.Mock).mockResolvedValue({ user: 'annotator' })
    ;(authPriv.getActiveRole as jest.Mock).mockResolvedValue('annotator')
    const res = await privilegesRoute.GET()
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.views).toBeDefined()
    expect(data.canConfigure).toBe(false)
  })

  it('returns canConfigure true for staff in admin mode', async () => {
    ;(authPriv.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    ;(authPriv.getActiveRole as jest.Mock).mockResolvedValue('admin')
    const res = await privilegesRoute.GET()
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.canConfigure).toBe(true)
  })
})

describe('API /api/privileges POST', () => {
  it('annotator receives 403', async () => {
    ;(authPriv.getSession as jest.Mock).mockResolvedValue({ user: 'annotator' })
    const res = await privilegesRoute.POST(
      new Request('http://localhost/api/privileges', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ annotator: { views: ['/'], canExport: false } }),
      })
    )
    expect(res.status).toBe(403)
  })

  it('customer receives 403', async () => {
    ;(authPriv.getSession as jest.Mock).mockResolvedValue({ user: 'customer' })
    const res = await privilegesRoute.POST(
      new Request('http://localhost/api/privileges', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ annotator: { views: ['/'], canExport: false } }),
      })
    )
    expect(res.status).toBe(403)
  })

  it('staff in annotator mode receives 403 (must switch to admin)', async () => {
    ;(authPriv.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    ;(authPriv.getActiveRole as jest.Mock).mockResolvedValue('annotator')
    const res = await privilegesRoute.POST(
      new Request('http://localhost/api/privileges', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ annotator: { views: ['/'], canExport: false } }),
      })
    )
    expect(res.status).toBe(403)
  })
})
