/**
 * User Story: Staff / Admin
 * Data annotation supply chain: staff manage the pipeline and privileges.
 * - Full access in admin mode
 * - Can configure annotator and customer privileges
 * - Can access pipeline view
 */
import { getViewsForRole, canExport, isPathAllowedForRole } from '@/lib/privileges'
import type { PrivilegesConfig } from '@/lib/privileges'

const CONFIG: PrivilegesConfig = {
  annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
  customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
}

describe('User Story: Staff / Admin (pipeline management)', () => {
  describe('Admin mode', () => {
    it('staff in admin mode sees all views including pipeline and privileges', () => {
      const views = getViewsForRole('staff', 'admin', CONFIG)
      expect(views).toContain('/admin/privileges')
      expect(views).toContain('/staff/pipeline')
      expect(views).toContain('/customer')
    })

    it('staff in admin mode can access any path', () => {
      expect(isPathAllowedForRole('/admin/privileges', 'staff', 'admin', CONFIG)).toBe(true)
      expect(isPathAllowedForRole('/staff/pipeline', 'staff', 'admin', CONFIG)).toBe(true)
      expect(isPathAllowedForRole('/customer', 'staff', 'admin', CONFIG)).toBe(true)
    })

    it('staff can always export', () => {
      expect(canExport('staff', 'admin', CONFIG)).toBe(true)
      expect(canExport('staff', 'annotator', CONFIG)).toBe(true)
    })
  })

  describe('Annotator mode (staff acting as annotator)', () => {
    it('staff in annotator mode sees annotator views only', () => {
      const views = getViewsForRole('staff', 'annotator', CONFIG)
      expect(views).not.toContain('/customer')
      expect(views).not.toContain('/admin/privileges')
      expect(views).toEqual(['/', '/dashboard', '/admin/tasks'])
    })

    it('staff in annotator mode cannot access Customer Portal', () => {
      expect(isPathAllowedForRole('/customer', 'staff', 'annotator', CONFIG)).toBe(false)
    })
  })
})
