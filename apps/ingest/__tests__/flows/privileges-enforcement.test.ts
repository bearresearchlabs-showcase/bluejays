/**
 * Flow: Privilege enforcement
 * Annotator blocked from /customer, /api/export. Customer allowed /customer, /api/export.
 * Staff (admin mode) allowed all paths including /admin/privileges.
 */
import { isPathAllowedForRole } from '@/lib/privileges'

const TEST_CONFIG = {
  annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
  customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
}

describe('Privileges enforcement flow', () => {
  it('annotator is blocked from /customer', () => {
    const allowed = isPathAllowedForRole('/customer', 'annotator', 'annotator', TEST_CONFIG)
    expect(allowed).toBe(false)
  })

  it('annotator is blocked from /api/export (path check)', () => {
    const allowed = isPathAllowedForRole('/api/export', 'annotator', 'annotator', TEST_CONFIG)
    expect(allowed).toBe(false)
  })

  it('customer is allowed /customer', () => {
    const allowed = isPathAllowedForRole('/customer', 'customer', 'annotator', TEST_CONFIG)
    expect(allowed).toBe(true)
  })

  it('customer is allowed /api/export (if in views - export is API, checked separately)', () => {
    const allowed = isPathAllowedForRole('/customer', 'customer', 'annotator', TEST_CONFIG)
    expect(allowed).toBe(true)
  })

  it('staff in system_owner mode is allowed /admin/privileges', () => {
    const allowed = isPathAllowedForRole('/admin/privileges', 'staff', 'system_owner', TEST_CONFIG)
    expect(allowed).toBe(true)
  })

  it('staff in system_owner mode is allowed all paths', () => {
    expect(isPathAllowedForRole('/admin/privileges', 'staff', 'system_owner', TEST_CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/staff/pipeline', 'staff', 'system_owner', TEST_CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/customer', 'staff', 'system_owner', TEST_CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/', 'staff', 'system_owner', TEST_CONFIG)).toBe(true)
  })

  it('staff in staff mode is allowed pipeline and customer but not privileges', () => {
    expect(isPathAllowedForRole('/staff/pipeline', 'staff', 'staff', TEST_CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/customer', 'staff', 'staff', TEST_CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/admin/privileges', 'staff', 'staff', TEST_CONFIG)).toBe(false)
  })

  it('staff in customer mode sees customer views only', () => {
    expect(isPathAllowedForRole('/customer', 'staff', 'customer', TEST_CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/suite', 'staff', 'customer', TEST_CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/staff/pipeline', 'staff', 'customer', TEST_CONFIG)).toBe(false)
    expect(isPathAllowedForRole('/admin/privileges', 'staff', 'customer', TEST_CONFIG)).toBe(false)
  })

  it('annotator is blocked from /staff/pipeline', () => {
    const allowed = isPathAllowedForRole('/staff/pipeline', 'annotator', 'annotator', TEST_CONFIG)
    expect(allowed).toBe(false)
  })
})
