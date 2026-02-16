/**
 * API: Export formats (json, csv, md, doccano)
 * @jest-environment node
 */
import { NextRequest } from 'next/server'

jest.mock('@/lib/auth', () => ({
  getSession: jest.fn(),
  getActiveRole: jest.fn(),
}))

jest.mock('@/lib/data', () => ({
  loadQueries: jest.fn(() => ({
    queries: [
      { number: 1, title: 'Q1', sql: 'SELECT 1', question: 'Test?', audit_status: 'Approved' },
      { number: 2, title: 'Q2', sql: 'SELECT 2', question: 'Test2?', audit_status: 'Ready to Audit' },
    ],
    error: null,
  })),
}))

const auth = require('@/lib/auth')
const exportRoute = require('@/app/api/export/route')

beforeEach(() => {
  ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'customer' })
  ;(auth.getActiveRole as jest.Mock).mockResolvedValue('annotator')
})

async function callExport(format: string) {
  const req = new NextRequest(`http://localhost/api/export?source=db-1&format=${format}`)
  return exportRoute.GET(req)
}

describe('API /api/export formats', () => {
  it('format=json returns JSON', async () => {
    const res = await callExport('json')
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.queries).toBeDefined()
    expect(data.queries.length).toBe(2)
  })

  it('format=csv returns CSV', async () => {
    const res = await callExport('csv')
    expect(res.status).toBe(200)
    const text = await res.text()
    expect(text).toContain('question_id')
    expect(text).toContain('SELECT 1')
  })

  it('format=md returns markdown', async () => {
    const res = await callExport('md')
    expect(res.status).toBe(200)
    const text = await res.text()
    expect(text.length).toBeGreaterThan(0)
    expect(res.headers.get('Content-Type')).toContain('markdown')
  })

  it('format=doccano returns JSONL', async () => {
    const res = await callExport('doccano')
    expect(res.status).toBe(200)
    const text = await res.text()
    const lines = text.trim().split('\n')
    expect(lines.length).toBe(2)
    const first = JSON.parse(lines[0])
    expect(first).toHaveProperty('text')
    expect(first).toHaveProperty('label')
    expect(first.text).toContain('Query 1')
    expect(first.label).toContain('Approved')
  })

  it('invalid format returns 400', async () => {
    const res = await callExport('invalid')
    expect(res.status).toBe(400)
  })
})
