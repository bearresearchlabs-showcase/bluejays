/**
 * API: Export access by role
 * Export = selling annotated data to customer. Only customer and staff can export.
 * @jest-environment node
 */
import { NextRequest } from 'next/server'

jest.mock('@/lib/auth', () => ({
  getSession: jest.fn(),
  getViewMode: jest.fn(),
}))

jest.mock('@/lib/data', () => ({
  loadQueries: jest.fn(() => ({ queries: [{ question_id: 1 }], error: null })),
}))

const authExport = require('@/lib/auth')
const exportRoute = require('@/app/api/export/route')

async function callExport(user: string, viewMode: string) {
  ;(authExport.getSession as jest.Mock).mockResolvedValue({ user })
  ;(authExport.getViewMode as jest.Mock).mockResolvedValue(viewMode)
  const req = new NextRequest('http://localhost/api/export?source=template&format=json')
  return exportRoute.GET(req)
}

describe('API /api/export — role-based access', () => {
  it('annotator receives 403 Forbidden', async () => {
    const res = await callExport('annotator', 'annotator')
    expect(res.status).toBe(403)
  })

  it('customer receives 200 and can export', async () => {
    const res = await callExport('customer', 'annotator')
    expect(res.status).toBe(200)
  })

  it('staff in admin mode receives 200', async () => {
    const res = await callExport('staff', 'admin')
    expect(res.status).toBe(200)
  })

  it('staff in annotator mode can still export (staff always has export)', async () => {
    const res = await callExport('staff', 'annotator')
    expect(res.status).toBe(200)
  })

  it('unauthenticated receives 401', async () => {
    ;(authExport.getSession as jest.Mock).mockResolvedValue(null)
    const req = new NextRequest('http://localhost/api/export?source=template&format=json')
    const res = await exportRoute.GET(req)
    expect(res.status).toBe(401)
  })
})
