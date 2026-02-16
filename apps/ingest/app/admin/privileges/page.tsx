'use client'

import { ViewSelector } from '@/components/ViewSelector'
import { SchemaViewWrapper } from '@/components/SchemaViewWrapper'
import Link from 'next/link'
import { useEffect, useState } from 'react'

const ALL_VIEWS = [
  { value: '/', label: 'Annotator' },
  { value: '/dashboard', label: 'Dashboard' },
  { value: '/suite', label: 'Databases' },
  { value: '/customer', label: 'Customer Portal' },
  { value: '/admin/tasks', label: 'Task Board' },
]

interface RolePrivileges {
  views: string[]
  canExport: boolean
}

interface PrivilegesConfig {
  annotator: RolePrivileges
  customer: RolePrivileges
}

export default function PrivilegesPage() {
  const [config, setConfig] = useState<PrivilegesConfig | null>(null)
  const [canConfigure, setCanConfigure] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/privileges')
      .then((r) => r.json())
      .then((data) => {
        if (data.config) setConfig(data.config)
        setCanConfigure(!!data.canConfigure)
      })
      .catch(() => setConfig(null))
  }, [])

  const toggleView = (role: 'annotator' | 'customer', view: string) => {
    if (!config) return
    const r = config[role]
    const next = r.views.includes(view)
      ? r.views.filter((v) => v !== view)
      : [...r.views, view]
    setConfig({ ...config, [role]: { ...r, views: next } })
  }

  const toggleExport = (role: 'annotator' | 'customer') => {
    if (!config) return
    const r = config[role]
    setConfig({ ...config, [role]: { ...r, canExport: !r.canExport } })
  }

  const save = async () => {
    if (!config || !canConfigure) return
    setSaving(true)
    setMessage(null)
    try {
      const res = await fetch('/api/privileges', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      const data = await res.json()
      if (!res.ok) {
        setMessage(data.error || 'Failed to save')
      } else {
        setMessage('Saved successfully')
      }
    } catch {
      setMessage('Failed to save')
    } finally {
      setSaving(false)
    }
  }

  if (!config) {
    return (
      <div className="container">
        <ViewSelector />
        <p>Loading…</p>
      </div>
    )
  }

  if (!canConfigure) {
    return (
      <div className="container">
        <ViewSelector />
        <nav style={{ marginBottom: '1.5rem' }}>
          <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
          <Link href="/customer" style={{ marginRight: '1rem' }}>Customer Portal</Link>
          <Link href="/admin/privileges" style={{ marginRight: '1rem' }}>Privileges</Link>
          <Link href="/logout">Log out</Link>
        </nav>
        <h1>Privileges</h1>
        <p style={{ color: 'var(--fg-muted)' }}>
          Switch to System owner mode to configure annotator and customer privileges.
        </p>
      </div>
    )
  }

  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '1.5rem' }}>
        <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/customer" style={{ marginRight: '1rem' }}>Customer Portal</Link>
        <Link href="/admin/tasks" style={{ marginRight: '1rem' }}>Task Board</Link>
        <Link href="/admin/privileges" style={{ marginRight: '1rem' }}>Privileges</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>
        Privilege Configuration
      </h1>
      <p style={{ color: 'var(--fg-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
        Configure which views annotators and customers can access. Staff always has full access.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <section
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '1.25rem',
          }}
        >
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 1rem 0' }}>
            Annotator (lowest privilege)
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '1rem' }}>
            Views available to annotator role:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
            {ALL_VIEWS.map((v) => (
              <label key={v.value} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.annotator.views.includes(v.value)}
                  onChange={() => toggleView('annotator', v.value)}
                />
                <span>{v.label}</span>
              </label>
            ))}
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={config.annotator.canExport}
              onChange={() => toggleExport('annotator')}
            />
            <span>Can export</span>
          </label>
        </section>

        <section
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '1.25rem',
          }}
        >
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 1rem 0' }}>
            Customer (mid privilege)
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '1rem' }}>
            Views available to customer role:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
            {ALL_VIEWS.map((v) => (
              <label key={v.value} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.customer.views.includes(v.value)}
                  onChange={() => toggleView('customer', v.value)}
                />
                <span>{v.label}</span>
              </label>
            ))}
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={config.customer.canExport}
              onChange={() => toggleExport('customer')}
            />
            <span>Can export</span>
          </label>
        </section>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={save}
            disabled={saving}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--accent)',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: saving ? 'not-allowed' : 'pointer',
              fontWeight: 600,
            }}
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
          {message && (
            <span style={{ fontSize: '0.875rem', color: message.includes('Failed') ? 'var(--error)' : 'var(--fg-muted)' }}>
              {message}
            </span>
          )}
        </div>
      </div>
      <SchemaViewWrapper />
    </div>
  )
}
