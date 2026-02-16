/**
 * Flow: Annotator submission
 * AnnotatorWorkbench loads from /api/queries and saves via POST /api/queries/sync.
 * Asserts sync payload structure and 401 when unauthenticated.
 */
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { AnnotatorWorkbench } from '@/components/AnnotatorWorkbench'

const mockFetch = jest.fn()

beforeEach(() => {
  mockFetch.mockReset()
  global.fetch = mockFetch
})

describe('Annotator submission flow', () => {
  it('loads sources and queries on mount', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({ sources: ['template', 'db-1'] }) })
      .mockResolvedValueOnce({
        json: () =>
          Promise.resolve({
            queries: [{ number: 1, title: 'Q1', sql: 'SELECT 1', question: 'Test' }],
          }),
      })

    render(<AnnotatorWorkbench />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/sources')
    })
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/api/queries?source='))
    })
  })

  it('calls sync with correct payload on save', async () => {
    const queries = [
      { number: 1, title: 'Q1', sql: 'SELECT 1', question: 'Test', question_id: 1 },
      { number: 2, title: 'Q2', sql: 'SELECT 2', question: 'Test2', question_id: 2 },
    ]
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({ sources: ['template'] }) })
      .mockResolvedValueOnce({ json: () => Promise.resolve({ queries }) })
      .mockResolvedValueOnce({
        json: () => Promise.resolve({ status: 'success', queries_count: 2 }),
      })

    render(<AnnotatorWorkbench />)

    await waitFor(() => expect(screen.queryByText(/Loading/)).not.toBeInTheDocument())

    const firstQuery = await screen.findByText(/1\. Test/)
    fireEvent.click(firstQuery)

    const saveBtn = await screen.findByRole('button', { name: /Save changes/i })
    fireEvent.click(saveBtn)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/queries/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: expect.stringContaining('"source":"template"'),
      })
    })
    const syncCall = mockFetch.mock.calls.find((c) => c[0] === '/api/queries/sync')
    expect(syncCall).toBeDefined()
    const body = JSON.parse(syncCall[1]?.body ?? '{}')
    expect(body.source).toBe('template')
    expect(body.format).toBe('json')
    expect(Array.isArray(body.content)).toBe(true)
  })

  it('handles 401 from sync (unauthenticated)', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({ sources: ['template'] }) })
      .mockResolvedValueOnce({
        json: () =>
          Promise.resolve({
            queries: [{ number: 1, title: 'Q1', sql: 'SELECT 1', question: 'Test' }],
          }),
      })
      .mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Unauthorized' }),
      })

    render(<AnnotatorWorkbench />)

    await waitFor(() => expect(screen.queryByText(/Loading/)).not.toBeInTheDocument())
    const firstQuery = await screen.findByText(/1\. Test/)
    fireEvent.click(firstQuery)
    const saveBtn = await screen.findByRole('button', { name: /Save changes/i })
    fireEvent.click(saveBtn)

    await waitFor(() => {
      expect(screen.getByText(/Unauthorized|Save failed/)).toBeInTheDocument()
    })
  })
})
