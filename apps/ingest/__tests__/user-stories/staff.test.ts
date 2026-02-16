/**
 * User Story: Staff / Admin (BDD)
 * Data annotation supply chain: staff manage the pipeline and privileges.
 * Staff can switch modes: Annotator | Staff | Customer | System owner.
 */
import { getViewsForRole, canExport, isPathAllowedForRole } from '@/lib/privileges'
import type { PrivilegesConfig } from '@/lib/privileges'

const CONFIG: PrivilegesConfig = {
  annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
  customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
}

describe('User Story: Staff (mode switching)', () => {
  describe('System owner mode (full access)', () => {
    it('staff in system_owner mode sees all views including pipeline and privileges', () => {
      const views = getViewsForRole('staff', 'system_owner', CONFIG)
      expect(views).toContain('/admin/privileges')
      expect(views).toContain('/staff/pipeline')
      expect(views).toContain('/customer')
    })

    it('staff in system_owner mode can access any path', () => {
      expect(isPathAllowedForRole('/admin/privileges', 'staff', 'system_owner', CONFIG)).toBe(true)
      expect(isPathAllowedForRole('/staff/pipeline', 'staff', 'system_owner', CONFIG)).toBe(true)
      expect(isPathAllowedForRole('/customer', 'staff', 'system_owner', CONFIG)).toBe(true)
    })
  })

  describe('Staff mode (pipeline, customer, no privileges)', () => {
    it('staff in staff mode sees pipeline and customer but not privileges', () => {
      const views = getViewsForRole('staff', 'staff', CONFIG)
      expect(views).toContain('/staff/pipeline')
      expect(views).toContain('/customer')
      expect(views).not.toContain('/admin/privileges')
    })

    it('staff in staff mode cannot access privileges config', () => {
      expect(isPathAllowedForRole('/admin/privileges', 'staff', 'staff', CONFIG)).toBe(false)
    })
  })

  describe('Customer mode (preview customer view)', () => {
    it('staff in customer mode sees customer views only', () => {
      const views = getViewsForRole('staff', 'customer', CONFIG)
      expect(views).toContain('/customer')
      expect(views).toContain('/suite')
      expect(views).not.toContain('/staff/pipeline')
      expect(views).not.toContain('/admin/privileges')
    })

    it('staff in customer mode cannot access pipeline or privileges', () => {
      expect(isPathAllowedForRole('/staff/pipeline', 'staff', 'customer', CONFIG)).toBe(false)
      expect(isPathAllowedForRole('/admin/privileges', 'staff', 'customer', CONFIG)).toBe(false)
    })
  })

  describe('Annotator mode (staff acting as annotator)', () => {
    it('staff in annotator mode sees annotator views only', () => {
      const views = getViewsForRole('staff', 'annotator', CONFIG)
      expect(views).not.toContain('/customer')
      expect(views).not.toContain('/admin/privileges')
      expect(views).toEqual(['/', '/dashboard', '/admin/tasks'])
    })

    it('staff in annotator mode cannot access Customer Portal or pipeline', () => {
      expect(isPathAllowedForRole('/customer', 'staff', 'annotator', CONFIG)).toBe(false)
      expect(isPathAllowedForRole('/staff/pipeline', 'staff', 'annotator', CONFIG)).toBe(false)
    })
  })

  describe('Export (all modes)', () => {
    it('staff can always export in any mode', () => {
      expect(canExport('staff', 'system_owner', CONFIG)).toBe(true)
      expect(canExport('staff', 'staff', CONFIG)).toBe(true)
      expect(canExport('staff', 'customer', CONFIG)).toBe(true)
      expect(canExport('staff', 'annotator', CONFIG)).toBe(true)
    })
  })
})
