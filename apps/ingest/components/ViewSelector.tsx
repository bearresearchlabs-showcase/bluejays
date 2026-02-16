'use client'

import { useRouter, usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'

const VIEW_LABELS: Record<string, string> = {
  '/': 'Annotator',
  '/dashboard': 'Dashboard',
  '/suite': 'Databases',
  '/customer': 'Customer Portal',
  '/admin/tasks': 'Task Board',
  '/admin/privileges': 'Privileges',
  '/staff': 'Staff',
  '/staff/pipeline': 'Pipeline',
  '/validate': 'Validate',
}

export function ViewSelector() {
  const router = useRouter()
  const pathname = usePathname()
  const [views, setViews] = useState<{ value: string; label: string }[]>([])
  const [role, setRole] = useState<'annotator' | 'staff' | 'customer' | 'system_owner'>('annotator')
  const [showRole, setShowRole] = useState(false)

  useEffect(() => {
    Promise.all([fetch('/api/me').then((r) => r.json()), fetch('/api/privileges').then((r) => r.json())])
      .then(([me, priv]) => {
        if (me.canSwitchRole ?? me.canSwitchMode) {
          setShowRole(true)
          const r = me.role ?? me.mode ?? 'annotator'
          setRole((r === 'admin' ? 'system_owner' : r) as 'annotator' | 'staff' | 'customer' | 'system_owner')
        }
        const viewPaths = priv.views || []
        setViews(
          viewPaths.map((v: string) => ({ value: v, label: VIEW_LABELS[v] || v }))
        )
      })
      .catch(() => setViews([{ value: '/', label: 'Annotator' }]))
  }, [role])

  const handleRoleChange = async (r: 'annotator' | 'staff' | 'customer' | 'system_owner') => {
    await fetch('/api/set-role', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: r }),
    })
    setRole(r)
    router.refresh()
  }

  const pathMap: Record<string, string> = {
    '/': '/',
    '/dashboard': '/dashboard',
    '/admin/tasks': '/admin/tasks',
    '/suite': '/suite',
    '/customer': '/customer',
    '/staff': '/staff',
    '/staff/pipeline': '/staff/pipeline',
    '/validate': '/validate',
  }
  const current = pathMap[pathname] ?? pathname

  return (
    <div className="mb-4 pb-4 border-b border-[var(--border)]">
      {showRole && (
        <div className="flex items-center gap-2 mb-2">
          <label className="text-xs font-semibold uppercase text-[var(--fg-muted)]">
            Role
          </label>
          <select
            data-testid="role-select"
            value={role}
            onChange={(e) => handleRoleChange(e.target.value as 'annotator' | 'staff' | 'customer' | 'system_owner')}
            className="px-3 py-1.5 rounded-md text-sm cursor-pointer bg-[var(--bg-card)] border border-[var(--border)] text-[var(--fg)]"
          >
            <option value="annotator">Annotator</option>
            <option value="staff">Staff</option>
            <option value="customer">Customer</option>
            <option value="system_owner">System owner</option>
          </select>
        </div>
      )}
      <div className="flex items-center gap-2">
        <label className="text-xs font-semibold uppercase text-[var(--fg-muted)]">
          View
        </label>
        <select
          value={current}
          onChange={(e) => e.target.value && router.push(e.target.value)}
          className="px-3 py-1.5 rounded-md text-sm cursor-pointer bg-[var(--bg-card)] border border-[var(--border)] text-[var(--fg)]"
        >
          {views.map((v) => (
            <option key={v.value} value={v.value}>
              {v.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
