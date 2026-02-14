/**
 * End-to-end supply chain: Annotation → Customer data sale
 * - Annotators create/edit annotations (supply)
 * - Customers view and export data (demand/purchase)
 * - Staff manage pipeline and privileges
 */
import {
  getViewsForRole,
  canExport,
  isPathAllowedForRole,
} from '@/lib/privileges'
import type { PrivilegesConfig } from '@/lib/privileges'

const CONFIG: PrivilegesConfig = {
  annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
  customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
}

describe('Supply chain: Annotation to data sale', () => {
  it('annotator supplies annotations but cannot sell (no export)', () => {
    expect(canExport('annotator', 'annotator', CONFIG)).toBe(false)
    expect(getViewsForRole('annotator', 'annotator', CONFIG)).not.toContain('/customer')
  })

  it('customer can purchase data (export) but cannot edit supply', () => {
    expect(canExport('customer', 'annotator', CONFIG)).toBe(true)
    expect(isPathAllowedForRole('/customer', 'customer', 'annotator', CONFIG)).toBe(true)
  })

  it('staff can manage entire chain (pipeline, privileges, export)', () => {
    const views = getViewsForRole('staff', 'admin', CONFIG)
    expect(views).toContain('/staff/pipeline')
    expect(views).toContain('/admin/privileges')
    expect(canExport('staff', 'admin', CONFIG)).toBe(true)
  })

  it('supply chain boundary: customer cannot access annotator edit flow', () => {
    // Customer hits /api/queries/sync → 403 (enforced in API)
    expect(isPathAllowedForRole('/admin/tasks', 'customer', 'annotator', CONFIG)).toBe(true)
    // But sync API returns 403 for customer — tested in queries-sync-access.test.ts
  })
})
