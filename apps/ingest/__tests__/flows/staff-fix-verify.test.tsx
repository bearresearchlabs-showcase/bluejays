/**
 * Flow: Staff fix and verify
 * TaskPipeline loads tasks, filters by audit status. Staff-only paths return 403 for annotator.
 */
import { render, screen, waitFor } from '@testing-library/react'
import { TaskPipeline } from '@/components/TaskPipeline'
import { isPathAllowedForRole } from '@/lib/privileges'

const mockFetch = jest.fn()

beforeEach(() => {
  mockFetch.mockReset()
  global.fetch = mockFetch
})

describe('Staff fix and verify flow', () => {
  it('TaskPipeline loads tasks from /api/queries', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({ sources: ['db-1'] }) })
      .mockResolvedValueOnce({
        json: () =>
          Promise.resolve({
            queries: [
              { question_id: 1, question: 'Q1', task_status: 'Submitted', audit_status: 'Ready to Audit' },
              { question_id: 2, question: 'Q2', task_status: 'Completed', audit_status: 'Approved' },
            ],
          }),
      })

    render(<TaskPipeline source="db-1" />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/sources')
    })
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/api/queries?source=db-1'))
    })
    await waitFor(() => {
      expect(screen.getByText(/Pipeline — Scale-style staging/i)).toBeInTheDocument()
    })
  })

  it('tasks are grouped by phase (audit_status maps to complete/review/attempt)', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({ sources: ['db-1'] }) })
      .mockResolvedValueOnce({
        json: () =>
          Promise.resolve({
            queries: [
              { question_id: 1, audit_status: 'Ready to Audit', task_status: 'Submitted' },
              { question_id: 2, audit_status: 'Approved', task_status: 'Completed' },
              { question_id: 3, audit_status: 'Rejected' },
            ],
          }),
      })

    render(<TaskPipeline source="db-1" />)

    await waitFor(() => expect(screen.queryByText(/Loading/)).not.toBeInTheDocument())

    expect(screen.getByText('Attempt')).toBeInTheDocument()
    expect(screen.getByText('Review')).toBeInTheDocument()
    expect(screen.getByText('Complete')).toBeInTheDocument()
    expect(screen.getByText('Rejected')).toBeInTheDocument()
  })

  it('annotator is blocked from staff-only path /staff/pipeline', () => {
    const config = {
      annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
      customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
    }
    const allowed = isPathAllowedForRole('/staff/pipeline', 'annotator', 'annotator', config)
    expect(allowed).toBe(false)
  })

  it('staff in admin mode is allowed /staff/pipeline', () => {
    const config = {
      annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
      customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
    }
    const allowed = isPathAllowedForRole('/staff/pipeline', 'staff', 'admin', config)
    expect(allowed).toBe(true)
  })
})
