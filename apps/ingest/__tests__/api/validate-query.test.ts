/**
 * API: Validate query - staff only, syntax validation, role/view resolution
 * @jest-environment node
 */
import { NextRequest } from 'next/server'

jest.mock('@/lib/auth', () => ({
  getSession: jest.fn(),
}))

jest.mock('@/lib/data', () => ({
  loadQueries: jest.fn(),
}))

jest.mock('@/lib/sql-executor', () => ({
  getPgConfig: jest.fn(() => null),
  explainQuery: jest.fn(),
  executeQuery: jest.fn(),
}))

const auth = require('@/lib/auth')
const data = require('@/lib/data')
const queryRoute = require('@/app/api/validate/query/route')
const batchRoute = require('@/app/api/validate/batch/route')

describe('API /api/validate/query GET', () => {
  it('returns 401 when unauthenticated', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue(null)
    const req = new NextRequest('http://localhost/api/validate/query?source=db-1&query=1')
    const res = await queryRoute.GET(req)
    expect(res.status).toBe(401)
  })

  it('returns 403 when annotator', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'annotator' })
    const req = new NextRequest('http://localhost/api/validate/query?source=db-1&query=1')
    const res = await queryRoute.GET(req)
    expect(res.status).toBe(403)
  })

  it('returns 400 when source missing', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    const req = new NextRequest('http://localhost/api/validate/query?query=1')
    const res = await queryRoute.GET(req)
    expect(res.status).toBe(400)
  })

  it('returns 404 when source not found', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    ;(data.loadQueries as jest.Mock).mockReturnValue({ queries: [], error: 'Not found' })
    const req = new NextRequest('http://localhost/api/validate/query?source=db-99&query=1')
    const res = await queryRoute.GET(req)
    expect(res.status).toBe(404)
  })

  it('returns validation result for valid SQL', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    ;(data.loadQueries as jest.Mock).mockReturnValue({
      queries: [{ number: 1, title: 'Q1', sql: 'SELECT 1 AS x;' }],
    })
    const req = new NextRequest(
      'http://localhost/api/validate/query?source=db-1&query=1&role=staff&view=/customer'
    )
    const res = await queryRoute.GET(req)
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.valid).toBe(true)
    expect(body.errors).toEqual([])
    expect(body.materializedView).toBe(false)
  })

  it('returns validation errors for invalid SQL', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    ;(data.loadQueries as jest.Mock).mockReturnValue({
      queries: [{ number: 1, title: 'Q1', sql: 'SELECT * FROM t WHERE (a = 1' }],
    })
    const req = new NextRequest('http://localhost/api/validate/query?source=db-1&query=1')
    const res = await queryRoute.GET(req)
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.valid).toBe(false)
    expect(body.errors.length).toBeGreaterThan(0)
  })
})

describe('API /api/validate/query POST', () => {
  it('returns 401 when unauthenticated', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue(null)
    const req = new NextRequest('http://localhost/api/validate/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sql: 'SELECT 1;' }),
    })
    const res = await queryRoute.POST(req)
    expect(res.status).toBe(401)
  })

  it('returns validation for inline sql', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    const req = new NextRequest('http://localhost/api/validate/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sql: 'SELECT 1 AS n;', role: 'staff', view: '/customer' }),
    })
    const res = await queryRoute.POST(req)
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.valid).toBe(true)
    expect(body.materializedView).toBe(false)
  })

  it('returns 400 when sql and source both missing', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    const req = new NextRequest('http://localhost/api/validate/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    const res = await queryRoute.POST(req)
    expect(res.status).toBe(400)
  })
})

describe('API /api/validate/batch POST', () => {
  it('returns 401 when unauthenticated', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue(null)
    const req = new NextRequest('http://localhost/api/validate/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source: 'db-1' }),
    })
    const res = await batchRoute.POST(req)
    expect(res.status).toBe(401)
  })

  it('returns batch results for all queries', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
    ;(data.loadQueries as jest.Mock).mockReturnValue({
      queries: [
        { number: 1, title: 'Q1', sql: 'SELECT 1;' },
        { number: 2, title: 'Q2', sql: 'SELECT * FROM t WHERE (x' },
      ],
    })
    const req = new NextRequest('http://localhost/api/validate/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source: 'db-1', role: 'staff', view: '/customer' }),
    })
    const res = await batchRoute.POST(req)
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.results).toHaveLength(2)
    expect(body.results[0].valid).toBe(true)
    expect(body.results[1].valid).toBe(false)
  })
})
