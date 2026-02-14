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
}

export function ViewSelector() {
  const router = useRouter()
  const pathname = usePathname()
  const [views, setViews] = useState<{ value: string; label: string }[]>([])
  const [mode, setMode] = useState<'annotator' | 'admin'>('annotator')
  const [showMode, setShowMode] = useState(false)

  useEffect(() => {
    Promise.all([fetch('/api/me').then((r) => r.json()), fetch('/api/privileges').then((r) => r.json())])
      .then(([me, priv]) => {
        if (me.canSwitchMode) {
          setShowMode(true)
          setMode((me.mode || 'annotator') as 'annotator' | 'admin')
        }
        const viewPaths = priv.views || []
        setViews(
          viewPaths.map((v: string) => ({ value: v, label: VIEW_LABELS[v] || v }))
        )
      })
      .catch(() => setViews([{ value: '/', label: 'Annotator' }]))
  }, [])

  const handleModeChange = async (m: 'annotator' | 'admin') => {
    await fetch('/api/set-mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: m }),
    })
    setMode(m)
    router.refresh()
  }

  const pathMap: Record<string, string> = {
    '/': '/',
    '/dashboard': '/dashboard',
    '/admin/tasks': '/admin/tasks',
    '/suite': '/suite',
    '/customer': '/customer',
  }
  const current = pathMap[pathname] ?? pathname

  return (
    <div className="mb-4 pb-4 border-b border-[var(--border)]">
      {showMode && (
        <div className="flex items-center gap-2 mb-2">
          <label className="text-xs font-semibold uppercase text-[var(--fg-muted)]">
            Mode
          </label>
          <select
            value={mode}
            onChange={(e) => handleModeChange(e.target.value as 'annotator' | 'admin')}
            className="px-3 py-1.5 rounded-md text-sm cursor-pointer bg-[var(--bg-card)] border border-[var(--border)] text-[var(--fg)]"
          >
            <option value="annotator">Annotator</option>
            <option value="admin">Admin</option>
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
