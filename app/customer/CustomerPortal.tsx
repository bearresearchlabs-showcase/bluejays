'use client'

import { useEffect, useState } from 'react'

export function CustomerPortal({ defaultSource }: { defaultSource?: string }) {
  const [sources, setSources] = useState<string[]>([])
  const [source, setSource] = useState(defaultSource || '')
  const [tasks, setTasks] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/sources')
      .then((r) => r.json())
      .then((d) => {
        const s = d.sources || ['template']
        setSources(s)
        if (!source && s.length) setSource(s.find((x: string) => x.startsWith('db-')) || s[0])
      })
      .catch(() => setSources(['template']))
  }, [])

  useEffect(() => {
    if (defaultSource && sources.includes(defaultSource)) setSource(defaultSource)
  }, [defaultSource, sources])

  const load = () => {
    if (!source) return
    setLoading(true)
    fetch(`/api/queries?source=${encodeURIComponent(source)}`)
      .then((r) => r.json())
      .then((d) => {
        setTasks(d.queries || [])
        setLoading(false)
      })
      .catch(() => {
        setTasks([])
        setLoading(false)
      })
  }

  const exportUrl = (fmt: string) => `/api/export?source=${encodeURIComponent(source)}&format=${fmt}`

  return (
    <div>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
            Database
          </label>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            style={{ padding: '0.5rem 0.875rem', background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--fg)', borderRadius: 6, fontSize: '0.875rem' }}
          >
            {sources.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <button
          onClick={load}
          style={{ padding: '0.5rem 0.875rem', background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 6, fontSize: '0.875rem', cursor: 'pointer', fontWeight: 500 }}
        >
          Load tasks
        </button>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <a
          href={exportUrl('csv')}
          style={{ padding: '0.5rem 0.875rem', background: 'var(--accent)', color: '#fff', borderRadius: 6, fontSize: '0.875rem', textDecoration: 'none', fontWeight: 500 }}
        >
          Export CSV
        </a>
        <a
          href={exportUrl('json')}
          style={{ padding: '0.5rem 0.875rem', background: 'var(--accent)', color: '#fff', borderRadius: 6, fontSize: '0.875rem', textDecoration: 'none', fontWeight: 500 }}
        >
          Export JSON
        </a>
      </div>
      {loading && <p style={{ color: 'var(--fg-muted)' }}>Loading...</p>}
      {!loading && tasks.length > 0 && (
        <div style={{ overflowX: 'auto', border: '1px solid var(--border)', borderRadius: 8 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Query</th>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Question</th>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Task Status</th>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Audit Status</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((t, i) => (
                <tr key={i} style={{ borderTop: '1px solid var(--border)' }}>
                  <td style={{ padding: '0.625rem 0.75rem' }}>Query {String((t as Record<string, unknown>).question_id ?? (t as Record<string, unknown>).number ?? '?')}</td>
                  <td style={{ padding: '0.625rem 0.75rem' }}>{String((t as Record<string, unknown>).question ?? (t as Record<string, unknown>).title ?? '').slice(0, 60)}</td>
                  <td style={{ padding: '0.625rem 0.75rem' }}>{String((t as Record<string, unknown>).task_status || 'Completed')}</td>
                  <td style={{ padding: '0.625rem 0.75rem' }}>{String((t as Record<string, unknown>).audit_status || 'Ready to Audit')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && tasks.length === 0 && source && (
        <p style={{ color: 'var(--fg-muted)' }}>Select database and click Load tasks.</p>
      )}
    </div>
  )
}
