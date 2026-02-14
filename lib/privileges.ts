/**
 * Privileges config: annotator < customer < staff/admin
 * - annotator: lowest privilege (annotation work only)
 * - customer: mid privilege (customer portal, export)
 * - staff: highest (full access + admin dashboard)
 * Staff can configure annotator and customer views via /admin/privileges
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

export function getViewsForRole(
  user: string,
  viewMode: string,
  config: PrivilegesConfig
): string[] {
  if (user === 'staff' && viewMode === 'admin') {
    return [...ALL_VIEWS.map((v) => v.value), '/admin/privileges', '/staff', '/staff/pipeline']
  }
  if (user === 'staff' && viewMode === 'annotator') {
    return config.annotator.views
  }
  if (user === 'customer') return config.customer.views
  return config.annotator.views
}

export function canExport(user: string, viewMode: string, config: PrivilegesConfig): boolean {
  if (user === 'staff') return true
  if (user === 'customer') return config.customer.canExport
  return config.annotator.canExport
}

export function isPathAllowedForRole(
  path: string,
  user: string,
  viewMode: string,
  config: PrivilegesConfig
): boolean {
  if (user === 'staff' && viewMode === 'admin') return true
  const views = getViewsForRole(user, viewMode, config)
  if (path === '/admin/privileges') return user === 'staff' && viewMode === 'admin'
  const base = path.split('?')[0].replace(/\/$/, '') || '/'
  return views.some((v) => v === base || base.startsWith(v + '/'))
}
