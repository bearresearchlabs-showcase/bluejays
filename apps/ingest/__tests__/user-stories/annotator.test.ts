/**
 * User Story: Annotator
 * Data annotation supply chain: annotators create and edit SQL annotations.
 * - Can access: Annotator, Dashboard, Task Board (configurable)
 * - Cannot access: Customer Portal, Export
 * - Cannot configure privileges
 */
import { getViewsForRole, canExport, isPathAllowedForRole } from '@/lib/privileges'
import type { PrivilegesConfig } from '@/lib/privileges'

const CONFIG: PrivilegesConfig = {
  annotator: { views: ['/', '/dashboard', '/admin/tasks'], canExport: false },
  customer: { views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'], canExport: true },
}

describe('User Story: Annotator (annotation supply chain)', () => {
  describe('Views', () => {
    it('annotator sees only annotator views (no Customer Portal)', () => {
      const views = getViewsForRole('annotator', 'annotator', CONFIG)
      expect(views).not.toContain('/customer')
      expect(views).not.toContain('/suite')
      expect(views).toContain('/')
      expect(views).toContain('/dashboard')
      expect(views).toContain('/admin/tasks')
    })

    it('annotator cannot access /customer path', () => {
      expect(isPathAllowedForRole('/customer', 'annotator', 'annotator', CONFIG)).toBe(false)
    })

    it('annotator can access annotator workbench', () => {
      expect(isPathAllowedForRole('/', 'annotator', 'annotator', CONFIG)).toBe(true)
    })

    it('annotator can access dashboard', () => {
      expect(isPathAllowedForRole('/dashboard', 'annotator', 'annotator', CONFIG)).toBe(true)
    })
  })

  describe('Export (selling data to customer)', () => {
    it('annotator cannot export — data sale is customer-facing', () => {
      expect(canExport('annotator', 'annotator', CONFIG)).toBe(false)
    })
  })

  describe('Privileges config', () => {
    it('annotator has no admin/privileges access', () => {
      expect(isPathAllowedForRole('/admin/privileges', 'annotator', 'annotator', CONFIG)).toBe(false)
    })
  })
})
