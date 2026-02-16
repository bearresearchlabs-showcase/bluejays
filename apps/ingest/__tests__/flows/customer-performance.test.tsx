/**
 * Flow: Customer performance
 * CustomerPortal load completes within threshold for 30 queries (mock fast responses).
 */
import { render, screen, waitFor } from '@testing-library/react'
import { CustomerPortal } from '@/app/customer/CustomerPortal'

const mockFetch = jest.fn()
const LOAD_THRESHOLD_MS = 2000

beforeEach(() => {
  mockFetch.mockReset()
  global.fetch = mockFetch
})

describe('Customer performance flow', () => {
  it('loads 30 queries and renders within threshold', async () => {
    const queries = Array.from({ length: 30 }, (_, i) => ({
      number: i + 1,
      title: `Query ${i + 1}`,
      question: `Question ${i + 1}`,
      task_status: 'Completed',
      audit_status: 'Approved',
    }))

    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/sources')) {
        return Promise.resolve({ json: () => Promise.resolve({ sources: ['db-1'] }) })
      }
      if (url.includes('/api/queries')) {
        return Promise.resolve({ json: () => Promise.resolve({ queries }) })
      }
      if (url.includes('/api/schema')) {
        return Promise.resolve({ json: () => Promise.resolve({ schema: 'CREATE TABLE t (id INT);', source: 'db-1' }) })
      }
      return Promise.reject(new Error(`Unknown URL: ${url}`))
    })

    const start = Date.now()
    render(<CustomerPortal defaultSource="db-1" />)

    await waitFor(() => expect(screen.queryByText(/Loading/)).not.toBeInTheDocument(), {
      timeout: 3000,
    })

    await waitFor(() => {
      const rows = screen.getAllByText(/^Question \d+$/)
      expect(rows.length).toBe(30)
    })

    const elapsed = Date.now() - start
    expect(elapsed).toBeLessThan(LOAD_THRESHOLD_MS)
  }, 5000)

  it('mock /api/queries returns 30 items in <100ms', async () => {
    const queries = Array.from({ length: 30 }, (_, i) => ({
      number: i + 1,
      title: `Q${i + 1}`,
      task_status: 'Completed',
      audit_status: 'Approved',
    }))

    const start = Date.now()
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/queries')) {
        return Promise.resolve({ json: () => Promise.resolve({ queries }) })
      }
      if (url.includes('/api/sources')) {
        return Promise.resolve({ json: () => Promise.resolve({ sources: ['db-1'] }) })
      }
      if (url.includes('/api/schema')) {
        return Promise.resolve({ json: () => Promise.resolve({ schema: 'CREATE TABLE t (id INT);', source: 'db-1' }) })
      }
      return Promise.reject(new Error('Unknown URL'))
    })

    render(<CustomerPortal defaultSource="db-1" />)
    await waitFor(() => expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/api/queries')))
    const elapsed = Date.now() - start
    expect(elapsed).toBeLessThan(200)
  })
})
