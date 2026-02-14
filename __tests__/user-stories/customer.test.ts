/**
 * User Story: Customer
 * Data annotation supply chain: customers buy annotated data.
 * - Can access: Customer Portal, Databases, Export
 * - Cannot edit queries (annotators do that)
 * - Cannot configure privileges
 */
import { getViewsForRole, canExport, isPathAllowedForRole } from '@/lib/privileges'
import type { PrivilegesConfig } from '@/lib/privileges'

const CONFIG: PrivilegesConfig = {
  annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
  customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
}

describe('User Story: Customer (data buyer)', () => {
  describe('Views', () => {
    it('customer sees Customer Portal and Databases', () => {
      const views = getViewsForRole('customer', 'annotator', CONFIG)
      expect(views).toContain('/customer')
      expect(views).toContain('/suite')
    })

    it('customer can access Customer Portal', () => {
      expect(isPathAllowedForRole('/customer', 'customer', 'annotator', CONFIG)).toBe(true)
    })

    it('customer can access Databases (suite)', () => {
      expect(isPathAllowedForRole('/suite', 'customer', 'annotator', CONFIG)).toBe(true)
    })
  })

  describe('Export (buying annotated data)', () => {
    it('customer can export — primary data purchase flow', () => {
      expect(canExport('customer', 'annotator', CONFIG)).toBe(true)
    })
  })

  describe('Privileges config', () => {
    it('customer has no admin/privileges access', () => {
      expect(isPathAllowedForRole('/admin/privileges', 'customer', 'annotator', CONFIG)).toBe(false)
    })

    it('customer has no staff pipeline access', () => {
      expect(isPathAllowedForRole('/staff/pipeline', 'customer', 'annotator', CONFIG)).toBe(false)
    })
  })
})
