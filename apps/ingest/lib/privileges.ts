/**
 * Privileges config: annotator < customer < staff < system_owner
 * - annotator: lowest privilege (annotation work only)
 * - customer: mid privilege (customer portal, export)
 * - staff: pipeline, customer, tasks (no privilege config)
 * - system_owner: full access including /admin/privileges
 * Staff can switch modes: Annotator | Staff | Customer | System owner
 */

import { readFileSync, writeFileSync, existsSync } from 'fs'
import { join } from 'path'

export const ALL_VIEWS = [
  { value: '/', label: 'Annotator' },
  { value: '/dashboard', label: 'Dashboard' },
  { value: '/suite', label: 'Databases' },
  { value: '/customer', label: 'Customer Portal' },
  { value: '/admin/tasks', label: 'Task Board' },
] as const

export type Role = 'annotator' | 'customer' | 'staff'

export interface RolePrivileges {
  views: string[]
  canExport: boolean
}

export interface PrivilegesConfig {
  annotator: RolePrivileges
  customer: RolePrivileges
}

const DEFAULT_CONFIG: PrivilegesConfig = {
  annotator: {
    views: ['/', '/dashboard', '/admin/tasks'],
    canExport: false,
  },
  customer: {
    views: ['/', '/dashboard', '/suite', '/customer', '/admin/tasks'],
    canExport: true,
  },
}

function getConfigPath(): string {
  return join(process.cwd(), 'data', 'privileges-config.json')
}

export function loadPrivilegesConfig(): PrivilegesConfig {
  const path = getConfigPath()
  if (!existsSync(path)) return DEFAULT_CONFIG
  try {
    const raw = readFileSync(path, 'utf-8')
    const parsed = JSON.parse(raw) as Partial<PrivilegesConfig>
    return {
      annotator: { ...DEFAULT_CONFIG.annotator, ...parsed.annotator },
      customer: { ...DEFAULT_CONFIG.customer, ...parsed.customer },
    }
  } catch {
    return DEFAULT_CONFIG
  }
}

export function savePrivilegesConfig(config: PrivilegesConfig): void {
  const path = getConfigPath()
  writeFileSync(path, JSON.stringify(config, null, 2), 'utf-8')
}

/** System owner = full access (admin). Staff = pipeline, customer, tasks (no privilege config). */
export function isSystemOwner(activeRole: string): boolean {
  return activeRole === 'system_owner' || activeRole === 'admin'
}

export function getViewsForRole(
  user: string,
  activeRole: string,
  config: PrivilegesConfig
): string[] {
  if (user === 'staff' && isSystemOwner(activeRole)) {
    return [...ALL_VIEWS.map((v) => v.value), '/admin/privileges', '/staff', '/staff/pipeline', '/validate']
  }
  if (user === 'staff' && activeRole === 'staff') {
    return [...ALL_VIEWS.map((v) => v.value), '/staff', '/staff/pipeline', '/validate']
  }
  if (user === 'staff' && activeRole === 'customer') {
    return config.customer.views
  }
  if (user === 'staff' && activeRole === 'annotator') {
    return config.annotator.views
  }
  if (user === 'customer') return config.customer.views
  return config.annotator.views
}

export function canExport(user: string, activeRole: string, config: PrivilegesConfig): boolean {
  if (user === 'staff') return true
  if (user === 'customer') return config.customer.canExport
  return config.annotator.canExport
}

export function isPathAllowedForRole(
  path: string,
  user: string,
  activeRole: string,
  config: PrivilegesConfig
): boolean {
  if (user === 'staff' && isSystemOwner(activeRole)) return true
  const views = getViewsForRole(user, activeRole, config)
  if (path === '/admin/privileges') return user === 'staff' && isSystemOwner(activeRole)
  const base = path.split('?')[0].replace(/\/$/, '') || '/'
  return views.some((v) => v === base || base.startsWith(v + '/'))
}
