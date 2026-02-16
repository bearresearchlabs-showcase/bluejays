/**
 * API: Scale-style datasets (v2)
 * GET /api/v2/datasets, task, delivery, tasks — structure and pagination
 * @jest-environment node
 */
import { NextRequest } from 'next/server'

jest.mock('@/lib/auth', () => ({
  getSession: jest.fn(),
}))

jest.mock('@/lib/data', () => ({
  discoverSources: jest.fn(() => ['template', 'db-1', 'db-2']),
  loadQueries: jest.fn((source: string) => {
    const count = source === 'template' ? 5 : 30
    const queries = Array.from({ length: count }, (_, i) => ({
      number: i + 1,
      title: `Query ${i + 1}`,
      sql: `SELECT ${i + 1}`,
      question: `Q${i + 1}`,
    }))
    return { queries, error: null }
  }),
}))

const auth = require('@/lib/auth')
const datasetsRoute = require('@/app/api/v2/datasets/route')
const taskRoute = require('@/app/api/v2/datasets/task/route')
const deliveryRoute = require('@/app/api/v2/datasets/delivery/route')
const tasksRoute = require('@/app/api/v2/datasets/tasks/route')

beforeEach(() => {
  ;(auth.getSession as jest.Mock).mockResolvedValue({ user: 'staff' })
})

describe('API /api/v2/datasets', () => {
  it('GET returns list of datasets (db-1..db-16)', async () => {
    const res = await datasetsRoute.GET()
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.datasets).toBeDefined()
    expect(Array.isArray(data.datasets)).toBe(true)
    expect(data.datasets.length).toBeGreaterThanOrEqual(1)
    expect(data.datasets[0]).toHaveProperty('dataset_id')
    expect(data.datasets[0]).toHaveProperty('name')
  })

  it('returns 401 when unauthenticated', async () => {
    ;(auth.getSession as jest.Mock).mockResolvedValue(null)
    const res = await datasetsRoute.GET()
    expect(res.status).toBe(401)
  })
})

describe('API /api/v2/datasets/task', () => {
  it('GET ?task_id=1&dataset=db-1 returns single task', async () => {
    const req = new NextRequest('http://localhost/api/v2/datasets/task?task_id=1&dataset=db-1')
    const res = await taskRoute.GET(req)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.task_id).toBe('db-1-1')
    expect(data.dataset).toBe('db-1')
    expect(data.delivery).toBe('default')
    expect(data.response).toBeDefined()
    expect(data.response.sql).toBe('SELECT 1')
    expect(data.response.title).toBe('Query 1')
  })

  it('returns 400 when task_id or dataset missing', async () => {
    const req = new NextRequest('http://localhost/api/v2/datasets/task?dataset=db-1')
    const res = await taskRoute.GET(req)
    expect(res.status).toBe(400)
  })
})

describe('API /api/v2/datasets/delivery', () => {
  it('GET ?delivery_id=db-1 returns tasks with pagination', async () => {
    const req = new NextRequest('http://localhost/api/v2/datasets/delivery?delivery_id=db-1')
    const res = await deliveryRoute.GET(req)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.delivery_id).toBeDefined()
    expect(data.dataset).toBe('db-1')
    expect(data.tasks).toBeDefined()
    expect(Array.isArray(data.tasks)).toBe(true)
    expect(data.tasks.length).toBe(30)
    expect(data.tasks[0].task_id).toBe('db-1-1')
    expect(data.tasks[0].response).toBeDefined()
  })

  it('supports next_token for pagination', async () => {
    const dataMock = require('@/lib/data')
    ;(dataMock.loadQueries as jest.Mock).mockReturnValue({
      queries: Array.from({ length: 150 }, (_, i) => ({
        number: i + 1,
        title: `Q${i + 1}`,
        sql: `SELECT ${i + 1}`,
      })),
      error: null,
    })
    const req = new NextRequest('http://localhost/api/v2/datasets/delivery?delivery_id=db-1')
    const res = await deliveryRoute.GET(req)
    const data = await res.json()
    expect(data.tasks.length).toBe(100)
    expect(data.next_token).toBeDefined()
  })
})

describe('API /api/v2/datasets/tasks', () => {
  it('GET ?dataset=db-1 returns search results', async () => {
    const req = new NextRequest('http://localhost/api/v2/datasets/tasks?dataset=db-1')
    const res = await tasksRoute.GET(req)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.tasks).toBeDefined()
    expect(data.tasks.length).toBeGreaterThanOrEqual(1)
    expect(data.tasks[0]).toHaveProperty('task_id')
    expect(data.tasks[0]).toHaveProperty('dataset')
    expect(data.tasks[0]).toHaveProperty('response')
  })
})
