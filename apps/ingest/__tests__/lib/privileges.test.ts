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

  it('returns all views including privileges for staff in system_owner mode', () => {
    const views = getViewsForRole('staff', 'system_owner', TEST_CONFIG)
    expect(views).toContain('/admin/privileges')
    expect(views).toContain('/staff/pipeline')
    expect(views).toContain('/customer')
  })

  it('returns staff views (no privileges) for staff in staff mode', () => {
    const views = getViewsForRole('staff', 'staff', TEST_CONFIG)
    expect(views).toContain('/staff/pipeline')
    expect(views).toContain('/customer')
    expect(views).not.toContain('/admin/privileges')
  })

  it('returns customer views for staff in customer mode', () => {
    const views = getViewsForRole('staff', 'customer', TEST_CONFIG)
    expect(views).toContain('/customer')
    expect(views).toContain('/suite')
    expect(views).not.toContain('/staff/pipeline')
    expect(views).not.toContain('/admin/privileges')
  })

  it('returns annotator views for staff in annotator mode', () => {
    const views = getViewsForRole('staff', 'annotator', TEST_CONFIG)
    expect(views).toEqual(['/', '/dashboard', '/admin/tasks'])
  })
})

describe('canExport', () => {
  it('staff can always export', () => {
    expect(canExport('staff', 'system_owner', TEST_CONFIG)).toBe(true)
    expect(canExport('staff', 'staff', TEST_CONFIG)).toBe(true)
    expect(canExport('staff', 'annotator', TEST_CONFIG)).toBe(true)
  })

  it('customer can export when config allows', () => {
    expect(canExport('customer', 'annotator', TEST_CONFIG)).toBe(true)
  })

  it('annotator cannot export by default', () => {
    expect(canExport('annotator', 'annotator', TEST_CONFIG)).toBe(false)
  })
})
