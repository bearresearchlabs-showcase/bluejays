/**
 * Unit tests for privileges config (Scale-style role hierarchy)
 */
import {
  getViewsForRole,
  canExport,
  type PrivilegesConfig,
} from '@/lib/privileges'

// Mock fs for tests - we need to test with a fixed config
const TEST_CONFIG: PrivilegesConfig = {
  annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
  customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
}

describe('getViewsForRole', () => {
  it('returns annotator views for annotator role', () => {
    const views = getViewsForRole('annotator', 'annotator', TEST_CONFIG)
    expect(views).toEqual(['/', '/dashboard', '/admin/tasks'])
  })

  it('returns customer views for customer role', () => {
    const views = getViewsForRole('customer', 'annotator', TEST_CONFIG)
    expect(views).toContain('/customer')
    expect(views).toContain('/suite')
  })

  it('returns all views including pipeline for staff in admin mode', () => {
    const views = getViewsForRole('staff', 'admin', TEST_CONFIG)
    expect(views).toContain('/admin/privileges')
    expect(views).toContain('/staff/pipeline')
  })

  it('returns annotator views for staff in annotator mode', () => {
    const views = getViewsForRole('staff', 'annotator', TEST_CONFIG)
    expect(views).toEqual(['/', '/dashboard', '/admin/tasks'])
  })
})

describe('canExport', () => {
  it('staff can always export', () => {
    expect(canExport('staff', 'admin', TEST_CONFIG)).toBe(true)
    expect(canExport('staff', 'annotator', TEST_CONFIG)).toBe(true)
  })

  it('customer can export when config allows', () => {
    expect(canExport('customer', 'annotator', TEST_CONFIG)).toBe(true)
  })

  it('annotator cannot export by default', () => {
    expect(canExport('annotator', 'annotator', TEST_CONFIG)).toBe(false)
  })
})
