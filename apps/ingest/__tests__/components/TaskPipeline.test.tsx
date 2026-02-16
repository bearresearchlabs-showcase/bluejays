/**
 * Component tests for TaskPipeline (Scale-style staging)
 */
import { render, screen } from '@testing-library/react'
import { TaskPipeline } from '@/components/TaskPipeline'

// Mock fetch for API calls
beforeEach(() => {
  global.fetch = jest.fn()
  ;(global.fetch as jest.Mock).mockImplementation((url: string) => {
    if (url.includes('/api/sources')) {
      return Promise.resolve({ json: () => Promise.resolve({ sources: ['template', 'db-1'] }) })
    }
    if (url.includes('/api/queries')) {
      return Promise.resolve({
        json: () =>
          Promise.resolve({
            queries: [
              { question_id: 1, question: 'Test query', task_status: 'Submitted', audit_status: 'Ready to Audit' },
            ],
          }),
      })
    }
    return Promise.reject(new Error('Unknown URL'))
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

describe('TaskPipeline', () => {
  it('renders database selector', async () => {
    render(<TaskPipeline />)
    expect(await screen.findByText(/Pipeline — Scale-style staging/i)).toBeInTheDocument()
  })

  it('shows Scale docs link', async () => {
    render(<TaskPipeline />)
    const link = await screen.findByRole('link', { name: /Scale Rapid Pipelines/i })
    expect(link).toHaveAttribute('href', 'https://scale.com/docs/rapid-or-pipelines')
  })
})
