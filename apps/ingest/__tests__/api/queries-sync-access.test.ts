/**
 * API: Queries sync (edit) access
 * Annotators and staff can edit; customers cannot (they only buy the data).
 * @jest-environment node
 */
jest.mock('@/lib/auth', () => ({
  getSession: jest.fn(),
}))

jest.mock('fs', () => ({
  ...jest.requireActual('fs'),
  writeFileSync: jest.fn(),
  existsSync: jest.fn(() => true),
  mkdirSync: jest.fn(),
}))

const authSync = require('@/lib/auth')
const syncRoute = require('@/app/api/queries/sync/route')

async function callSync(user: string, body: object) {
  ;(authSync.getSession as jest.Mock).mockResolvedValue({ user })
  return syncRoute.POST(
    new Request('http://localhost/api/queries/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source: 'template',
        format: 'json',
        content: [{ question_id: 1, question: 'Test', SQL: 'SELECT 1' }],
        ...body,
      }),
    })
  )
}

describe('API /api/queries/sync — edit access', () => {
  it('annotator can sync (edit queries)', async () => {
    const res = await callSync('annotator', {})
    expect(res.status).toBe(200)
  })

  it('staff can sync', async () => {
    const res = await callSync('staff', {})
    expect(res.status).toBe(200)
  })

  it('customer receives 403 — cannot edit (supply chain boundary)', async () => {
    const res = await callSync('customer', {})
    expect(res.status).toBe(403)
    const data = await res.json()
    expect(data.error).toMatch(/customer/i)
  })
})
