'use client'

import { useRouter, usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'

const VIEWS = [
  { value: '/staff', label: 'Staff' },
  { value: '/', label: 'Annotator' },
  { value: '/admin/tasks', label: 'Task Board' },
  { value: '/dashboard', label: 'Dashboard' },
  { value: '/suite', label: 'Full Suite' },
  { value: '/customer', label: 'Customer Portal' },
]

export function ViewSelector() {
  const router = useRouter()
  const pathname = usePathname()
  const [views, setViews] = useState(VIEWS)
  const [mode, setMode] = useState<'annotator' | 'admin'>('annotator')
  const [showMode, setShowMode] = useState(false)

  useEffect(() => {
    fetch('/api/me')
      .then((r) => r.json())
      .then((me) => {
        if (me.canSwitchMode) {
          setShowMode(true)
          setMode((me.mode || 'annotator') as 'annotator' | 'admin')
        }
        if (me.mode === 'annotator' || me.user === 'annotator') {
          setViews(VIEWS.filter((v) => !['/dashboard', '/suite', '/customer'].includes(v.value)))
        } else if (me.user === 'customer') {
          setViews(VIEWS.filter((v) => ['/suite', '/customer'].includes(v.value)))
        }
      })
      .catch(() => {})
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
    '/staff': '/staff',
    '/admin/tasks': '/admin/tasks',
    '/suite': '/suite',
    '/customer': '/customer',
  }
  const current = pathMap[pathname] ?? pathname

  return (
    <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
      {showMode && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', textTransform: 'uppercase' }}>
            Mode
          </label>
          <select
            value={mode}
            onChange={(e) => handleModeChange(e.target.value as 'annotator' | 'admin')}
            style={{
              padding: '0.4rem 0.75rem',
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              color: 'var(--fg)',
              borderRadius: 6,
              fontSize: '0.875rem',
              cursor: 'pointer',
            }}
          >
            <option value="annotator">Annotator</option>
            <option value="admin">Admin</option>
          </select>
        </div>
      )}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', textTransform: 'uppercase' }}>
          View
        </label>
        <select
          value={current}
          onChange={(e) => e.target.value && router.push(e.target.value)}
          style={{
            padding: '0.4rem 0.75rem',
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            color: 'var(--fg)',
            borderRadius: 6,
            fontSize: '0.875rem',
            cursor: 'pointer',
          }}
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
