'use client'

import { useEffect, useState } from 'react'
import { ViewSelector } from '@/components/ViewSelector'
import { ValidationSidePanel, type ValidationResult } from '@/components/ValidationSidePanel'
import Link from 'next/link'

const ROLES = [
  { value: 'annotator', label: 'Annotator' },
  { value: 'staff', label: 'Staff' },
  { value: 'customer', label: 'Customer' },
  { value: 'system_owner', label: 'System owner' },
] as const

const VIEWS = [
  { value: '/', label: 'Annotator' },
  { value: '/dashboard', label: 'Dashboard' },
  { value: '/suite', label: 'Databases' },
  { value: '/customer', label: 'Customer Portal' },
  { value: '/admin/tasks', label: 'Task Board' },
  { value: '/admin/privileges', label: 'Privileges' },
  { value: '/staff/pipeline', label: 'Pipeline' },
] as const

export default function ValidatePage() {
  const [sources, setSources] = useState<string[]>([])
  const [source, setSource] = useState('')
  const [role, setRole] = useState('staff')
  const [view, setView] = useState('/customer')
  const [queries, setQueries] = useState<Record<string, unknown>[]>([])
  const [batchResults, setBatchResults] = useState<Record<number, { valid: boolean; materializedView: boolean }>>({})
  const [selectedQuery, setSelectedQuery] = useState<Record<string, unknown> | null>(null)
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [batchLoading, setBatchLoading] = useState(false)

  useEffect(() => {
    fetch('/api/sources')
      .then((r) => r.json())
      .then((d) => {
        const s = d.sources ?? []
        setSources(s)
        setSource((prev) => (prev ? prev : s.find((x: string) => x.startsWith('db-')) ?? s[0] ?? ''))
      })
      .catch(() => setSources([]))
  }, [])

  useEffect(() => {
    if (!source) return
    fetch(`/api/queries?source=${encodeURIComponent(source)}`)
      .then((r) => r.json())
      .then((d) => setQueries(d.queries ?? []))
      .catch(() => setQueries([]))
  }, [source])

  useEffect(() => {
    if (!source || queries.length === 0) return
    let cancelled = false
    const run = async () => {
      setBatchLoading(true)
      try {
        const res = await fetch('/api/validate/batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source, role, view }),
        })
        const d = await res.json()
        if (cancelled) return
        const map: Record<number, { valid: boolean; materializedView: boolean }> = {}
        for (const r of d.results ?? []) {
          map[r.queryNumber] = { valid: r.valid, materializedView: r.materializedView }
        }
        setBatchResults(map)
      } catch {
        if (!cancelled) setBatchResults({})
      } finally {
        if (!cancelled) setBatchLoading(false)
      }
    }
    run()
    return () => { cancelled = true }
  }, [source, role, view, queries.length])

  const handleSelectQuery = (q: Record<string, unknown>) => {
    setSelectedQuery(q)
    setLoading(true)
    setValidationResult(null)
    const num = (q.number ?? q.question_id) as number
    const params = new URLSearchParams({
      source,
      query: String(num),
      role,
      view,
    })
    fetch(`/api/validate/query?${params}`)
      .then((r) => r.json())
      .then((data) => {
        setValidationResult({
          valid: data.valid,
          errors: data.errors ?? [],
          warnings: data.warnings ?? [],
          materializedView: data.materializedView ?? false,
          executionResult: data.executionResult,
          executionTimeMs: data.executionTimeMs,
        })
      })
      .catch(() => setValidationResult(null))
      .finally(() => setLoading(false))
  }

  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '2rem' }}>
        <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/" style={{ marginRight: '1rem' }}>Annotator</Link>
        <Link href="/suite" style={{ marginRight: '1rem' }}>Databases</Link>
        <Link href="/customer" style={{ marginRight: '1rem' }}>Customer Portal</Link>
        <Link href="/admin/tasks" style={{ marginRight: '1rem' }}>Task Board</Link>
        <Link href="/validate" style={{ marginRight: '1rem' }}>Validate</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Query Validation</h1>
      <p style={{ color: 'var(--fg-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
        Validate SQL per role and view. Select a query to see material view and outputs.
      </p>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>
            Database
          </label>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            style={{
              padding: '0.5rem 0.75rem',
              minWidth: 140,
              background: 'var(--bg)',
              border: '1px solid var(--border)',
              color: 'var(--fg)',
              borderRadius: 6,
              fontSize: '0.875rem',
            }}
          >
            {sources.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>
            Role
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={{
              padding: '0.5rem 0.75rem',
              minWidth: 120,
              background: 'var(--bg)',
              border: '1px solid var(--border)',
              color: 'var(--fg)',
              borderRadius: 6,
              fontSize: '0.875rem',
            }}
          >
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>
            View
          </label>
          <select
            value={view}
            onChange={(e) => setView(e.target.value)}
            style={{
              padding: '0.5rem 0.75rem',
              minWidth: 140,
              background: 'var(--bg)',
              border: '1px solid var(--border)',
              color: 'var(--fg)',
              borderRadius: 6,
              fontSize: '0.875rem',
            }}
          >
            {VIEWS.map((v) => (
              <option key={v.value} value={v.value}>{v.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '1.5rem', alignItems: 'start' }}>
        <div>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Queries</h2>
          {batchLoading && <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>Loading validation…</p>}
          <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {queries.map((q, idx) => {
              const num = (q.number ?? q.question_id ?? idx + 1) as number
              const title = String(q.title ?? q.question ?? `Query ${num}`).slice(0, 50)
              const br = batchResults[num]
              const isSelected = selectedQuery === q
              return (
                <li key={num}>
                  <button
                    type="button"
                    onClick={() => handleSelectQuery(q)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      width: '100%',
                      padding: '0.5rem 0.75rem',
                      marginBottom: '0.25rem',
                      background: isSelected ? 'var(--bg)' : 'var(--bg-card)',
                      border: `1px solid ${isSelected ? 'var(--accent)' : 'var(--border)'}`,
                      borderRadius: 6,
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontSize: '0.875rem',
                      color: 'var(--fg)',
                    }}
                  >
                    {br && (
                      <span
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: 4,
                          background: br.valid ? '#22c55e' : '#ef4444',
                          flexShrink: 0,
                        }}
                      />
                    )}
                    <span style={{ fontWeight: 500 }}>Query {num}</span>
                    <span style={{ color: 'var(--fg-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {title}
                    </span>
                    {br?.materializedView && (
                      <span style={{ fontSize: '0.7rem', color: 'var(--accent)', flexShrink: 0 }}>MV</span>
                    )}
                  </button>
                </li>
              )
            })}
          </ul>
          {queries.length === 0 && !batchLoading && (
            <p style={{ color: 'var(--fg-muted)', fontSize: '0.8125rem' }}>No queries. Select a database.</p>
          )}
        </div>
        <ValidationSidePanel
          result={validationResult}
          loading={loading}
          queryTitle={selectedQuery ? `Query ${(selectedQuery.number ?? selectedQuery.question_id) ?? ''}` : undefined}
        />
      </div>
    </div>
  )
}
