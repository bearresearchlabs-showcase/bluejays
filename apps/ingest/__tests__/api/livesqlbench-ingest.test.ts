/**
 * API: LiveSQLBench ingest — staff only
 * @jest-environment node
 */
import { NextRequest } from 'next/server'

jest.mock('@/lib/auth', () => ({
  getSession: jest.fn(),
}))

const auth = require('@/lib/auth')
const route = require('@/app/api/ingest/livesqlbench/route')

async function callPost(user: string | null, body: unknown) {
  ;(auth.getSession as jest.Mock).mockResolvedValue(user ? { user } : null)
  const req = new NextRequest('http://localhost/api/ingest/livesqlbench', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return route.POST(req)
}

const validInstance = {
  instance_id: 'alien_1',
  selected_database: 'alien',
  query: 'Show me signals by category.',
  category: 'Query',
  difficulty_tier: 'Simple',
}

describe('API /api/ingest/livesqlbench — staff only', () => {
  it('unauthenticated receives 401', async () => {
    const res = await callPost(null, validInstance)
    expect(res.status).toBe(401)
  })

  it('annotator receives 403', async () => {
    const res = await callPost('annotator', validInstance)
    expect(res.status).toBe(403)
  })

  it('customer receives 403', async () => {
    const res = await callPost('customer', validInstance)
    expect(res.status).toBe(403)
  })

  it('staff receives 200 and parsed summary', async () => {
    const res = await callPost('staff', validInstance)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.ok).toBe(true)
    expect(data.ingested).toBe(1)
    expect(data.databases).toContain('alien')
    expect(data.categories).toContain('Query')
  })

  it('staff can ingest array of instances', async () => {
    const res = await callPost('staff', [validInstance, { ...validInstance, instance_id: 'alien_2' }])
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.ingested).toBe(2)
  })

  it('invalid JSON body returns 400', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    const req = new NextRequest('http://localhost/api/ingest/livesqlbench', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: 'not json',
    })
    const res = await route.POST(req)
    expect(res.status).toBe(400)
  })

  it('non-instance body returns 400', async () => {
    const res = await callPost('staff', { foo: 'bar' })
    expect(res.status).toBe(400)
  })
})
