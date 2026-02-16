/**
 * Flow: Customer view and visualizations
 * CustomerPortal loads /api/queries?source=db-1, tasks render, export URLs correct.
 */
import { render, screen, waitFor } from '@testing-library/react'
import { CustomerPortal } from '@/app/customer/CustomerPortal'

const mockFetch = jest.fn()

beforeEach(() => {
  mockFetch.mockReset()
  global.fetch = mockFetch
})

describe('Customer view flow', () => {
  it('CustomerPortal loads tasks from /api/queries?source=db-1', async () => {
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/sources')) return Promise.resolve({ json: () => Promise.resolve({ sources: ['db-1', 'template'] }) })
      if (url.includes('/api/queries')) return Promise.resolve({ json: () => Promise.resolve({ queries: [{ number: 1, title: 'Q1', question: 'Test query', task_status: 'Completed', audit_status: 'Approved' }, { number: 2, title: 'Q2', question: 'Test query 2', task_status: 'Submitted', audit_status: 'Ready to Audit' }] }) })
      if (url.includes('/api/schema')) return Promise.resolve({ json: () => Promise.resolve({ schema: 'CREATE TABLE t (id INT);', source: 'db-1' }) })
      return Promise.reject(new Error(`Unknown URL: ${url}`))
    })

    render(<CustomerPortal defaultSource="db-1" />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/sources')
    })
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/api/queries?source=db-1'))
    })
    await waitFor(() => {
      expect(screen.getByText(/Select database for annotation tasks/i)).toBeInTheDocument()
    })
  })

  it('tasks render in table with Query, Question, Task Status, Audit Status columns', async () => {
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/sources')) return Promise.resolve({ json: () => Promise.resolve({ sources: ['db-1'] }) })
      if (url.includes('/api/queries')) return Promise.resolve({ json: () => Promise.resolve({ queries: [{ number: 1, title: 'Multi-Window', question: 'Test query', task_status: 'Completed', audit_status: 'Approved' }] }) })
      if (url.includes('/api/schema')) return Promise.resolve({ json: () => Promise.resolve({ schema: 'CREATE TABLE t (id INT);', source: 'db-1' }) })
      return Promise.reject(new Error(`Unknown URL: ${url}`))
    })

    render(<CustomerPortal defaultSource="db-1" />)

    await waitFor(() => expect(screen.queryByText(/Loading/)).not.toBeInTheDocument())

    expect(screen.getByText('Query')).toBeInTheDocument()
    expect(screen.getByText('Question')).toBeInTheDocument()
    expect(screen.getAllByText('Task Status').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Audit Status').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(/Test query/)).toBeInTheDocument()
  })

  it('renders Task Status, Audit Status, and Completion charts when tasks loaded', async () => {
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/sources')) return Promise.resolve({ json: () => Promise.resolve({ sources: ['db-1'] }) })
      if (url.includes('/api/queries')) return Promise.resolve({ json: () => Promise.resolve({ queries: [{ number: 1, title: 'Q1', task_status: 'Completed', audit_status: 'Approved' }, { number: 2, title: 'Q2', task_status: 'Submitted', audit_status: 'Ready to Audit' }] }) })
      if (url.includes('/api/schema')) return Promise.resolve({ json: () => Promise.resolve({ schema: 'CREATE TABLE t (id INT);', source: 'db-1' }) })
      return Promise.reject(new Error(`Unknown URL: ${url}`))
    })

    render(<CustomerPortal defaultSource="db-1" />)

    await waitFor(() => expect(screen.queryByText(/Loading/)).not.toBeInTheDocument())

    expect(screen.getAllByText('Task Status').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Audit Status').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Completion')).toBeInTheDocument()
  })

  it('export URLs are correct for CSV and JSON', async () => {
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/sources')) return Promise.resolve({ json: () => Promise.resolve({ sources: ['db-1'] }) })
      if (url.includes('/api/queries')) return Promise.resolve({ json: () => Promise.resolve({ queries: [{ number: 1, title: 'Q1', task_status: 'Completed', audit_status: 'Approved' }] }) })
      if (url.includes('/api/schema')) return Promise.resolve({ json: () => Promise.resolve({ schema: 'CREATE TABLE t (id INT);', source: 'db-1' }) })
      return Promise.reject(new Error(`Unknown URL: ${url}`))
    })

    render(<CustomerPortal defaultSource="db-1" />)

    await waitFor(() => expect(screen.queryByText(/Loading/)).not.toBeInTheDocument())

    const csvLink = screen.getByRole('link', { name: /Export CSV/i })
    const jsonLink = screen.getByRole('link', { name: /Export JSON/i })

    expect(csvLink).toHaveAttribute('href', '/api/export?source=db-1&format=csv')
    expect(jsonLink).toHaveAttribute('href', '/api/export?source=db-1&format=json')
  })
})
