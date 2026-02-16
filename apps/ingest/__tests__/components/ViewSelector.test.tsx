/**
 * ViewSelector: role-based view options
 */
import { render, screen } from '@testing-library/react'
import { ViewSelector } from '@/components/ViewSelector'

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn(), refresh: jest.fn() }),
  usePathname: () => '/',
}))

beforeEach(() => {
  global.fetch = jest.fn()
  ;(global.fetch as jest.Mock).mockImplementation((url: string) => {
    if (url.includes('/api/me')) {
      return Promise.resolve({
        json: () => Promise.resolve({ user: 'annotator', canSwitchRole: false, role: 'annotator' }),
      })
    }
    if (url.includes('/api/privileges')) {
      return Promise.resolve({
        json: () =>
          Promise.resolve({
            views: ['/', '/dashboard', '/admin/tasks'],
            canConfigure: false,
          }),
      })
    }
    return Promise.reject(new Error('Unknown URL'))
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

describe('ViewSelector', () => {
  it('renders View label', async () => {
    render(<ViewSelector />)
    expect(await screen.findByText(/View/i)).toBeInTheDocument()
  })

  it('fetches me and privileges on mount', async () => {
    render(<ViewSelector />)
    await screen.findByText(/View/i)
    expect(global.fetch).toHaveBeenCalledWith('/api/me')
    expect(global.fetch).toHaveBeenCalledWith('/api/privileges')
  })

  it('does not show Role selector for annotator (no canSwitchRole)', async () => {
    render(<ViewSelector />)
    await screen.findByText(/View/i)
    expect(screen.queryByText(/Role/i)).not.toBeInTheDocument()
  })
})
