'use client'

import { useEffect, useState, useMemo } from 'react'

const SQL_CELL_STYLE: React.CSSProperties = {
  padding: '0.625rem 0.75rem',
  fontFamily: 'monospace',
  fontSize: '0.75rem',
  maxWidth: 200,
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap' as const,
}
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import { SchemaView } from '@/components/SchemaView'
import { ToolsSection } from '@/components/ToolsSection'

const CHART_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280']

function useChartData(tasks: Record<string, unknown>[]) {
  return useMemo(() => {
    const taskCounts: Record<string, number> = {}
    const auditCounts: Record<string, number> = {}
    let completed = 0
    for (const t of tasks) {
      const ts = String((t as Record<string, unknown>).task_status || 'Completed')
      taskCounts[ts] = (taskCounts[ts] ?? 0) + 1
      if (ts.toLowerCase().includes('complet') || ts === 'Submitted') completed++
      const as = String((t as Record<string, unknown>).audit_status || 'Ready to Audit')
      auditCounts[as] = (auditCounts[as] ?? 0) + 1
    }
    const taskData = Object.entries(taskCounts).map(([name, value]) => ({ name, value }))
    const auditData = Object.entries(auditCounts).map(([name, value]) => ({ name, value }))
    const progressData = [
      { name: 'Completed', value: completed, fill: '#22c55e' },
      { name: 'Remaining', value: Math.max(0, tasks.length - completed), fill: '#3b82f6' },
    ]
    return { taskData, auditData, progressData }
  }, [tasks])
}

export function CustomerPortal({ defaultSource }: { defaultSource?: string }) {
  const [sources, setSources] = useState<string[]>([])
  const [source, setSource] = useState(defaultSource || '')
  const [tasks, setTasks] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedSqlKey, setExpandedSqlKey] = useState<string | null>(null)
  const [filterTaskStatus, setFilterTaskStatus] = useState<string | null>(null)
  const [filterAuditStatus, setFilterAuditStatus] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/sources')
      .then((r) => r.json())
      .then((d) => {
        const s = d.sources || ['template']
        setSources(s)
        setSource((prev) => (prev ? prev : (s.find((x: string) => x.startsWith('db-')) || s[0])))
      })
      .catch(() => setSources(['template']))
  }, [])

  useEffect(() => {
    if (defaultSource && sources.includes(defaultSource)) {
      queueMicrotask(() => setSource(defaultSource))
    }
  }, [defaultSource, sources])

  // Auto-load tasks when source changes (no manual "Load tasks" click needed)
  useEffect(() => {
    if (!source) return
    queueMicrotask(() => setLoading(true))
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
  }, [source])

  const exportUrl = (fmt: string) => `/api/export?source=${encodeURIComponent(source)}&format=${fmt}`
  const { taskData, auditData, progressData } = useChartData(tasks)
  const filteredTasks = tasks.filter((t) => {
    const ts = String((t as Record<string, unknown>).task_status || 'Completed')
    const as = String((t as Record<string, unknown>).audit_status || 'Ready to Audit')
    if (filterTaskStatus && ts !== filterTaskStatus) return false
    if (filterAuditStatus && as !== filterAuditStatus) return false
    return true
  })
  const hasFilter = filterTaskStatus !== null || filterAuditStatus !== null

  return (
    <div>
      <section style={{ marginBottom: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h2 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>
          Select database for annotation tasks
        </h2>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '1rem' }}>
          Choose a database to view its query tasks. Tasks load automatically when you change the selection.
        </p>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div>
            <label htmlFor="db-select" style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>
              Database ({sources.length} available)
            </label>
            <select
              id="db-select"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              style={{ padding: '0.5rem 0.875rem', minWidth: 140, background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--fg)', borderRadius: 6, fontSize: '0.875rem' }}
            >
              {sources.map((s) => (
                <option key={s} value={s}>{s === 'template' ? 'template (canonical)' : s}</option>
              ))}
            </select>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
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
        </div>
      </section>
      {loading && <p style={{ color: 'var(--fg-muted)', fontSize: '0.875rem' }}>Loading tasks…</p>}
      {!loading && tasks.length > 0 && (
        <>
        {hasFilter && (
          <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>
              Filter: {filterTaskStatus && `Task: ${filterTaskStatus}`}
              {filterTaskStatus && filterAuditStatus && ' · '}
              {filterAuditStatus && `Audit: ${filterAuditStatus}`}
            </span>
            <button
              type="button"
              onClick={() => { setFilterTaskStatus(null); setFilterAuditStatus(null) }}
              style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', borderRadius: 4, border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--fg)', cursor: 'pointer' }}
            >
              Clear filter
            </button>
          </div>
        )}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem', minHeight: 200 }}>
            <h3 style={{ fontSize: '0.8125rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg-muted)' }}>Task Status <span style={{ fontWeight: 400 }}>(click to filter)</span></h3>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={taskData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={60}
                  paddingAngle={2}
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                  onClick={(data) => setFilterTaskStatus(data?.name ?? null)}
                >
                  {taskData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} style={{ cursor: 'pointer' }} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem', minHeight: 200 }}>
            <h3 style={{ fontSize: '0.8125rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg-muted)' }}>Audit Status <span style={{ fontWeight: 400 }}>(click to filter)</span></h3>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={auditData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={60}
                  paddingAngle={2}
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                  onClick={(data) => setFilterAuditStatus(data?.name ?? null)}
                >
                  {auditData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} style={{ cursor: 'pointer' }} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1rem', minHeight: 200 }}>
            <h3 style={{ fontSize: '0.8125rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg-muted)' }}>Completion</h3>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={progressData} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={70} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" radius={4} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div style={{ overflowX: 'auto', border: '1px solid var(--border)', borderRadius: 8 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Query</th>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Question</th>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>SQL</th>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Task Status</th>
                <th style={{ padding: '0.625rem 0.75rem', textAlign: 'left', color: 'var(--fg-muted)', fontWeight: 500 }}>Audit Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredTasks.map((t, i) => {
                const qid = String((t as Record<string, unknown>).question_id ?? (t as Record<string, unknown>).number ?? i)
                const sql = String((t as Record<string, unknown>).sql ?? (t as Record<string, unknown>).SQL ?? '')
                const sqlPreview = sql ? sql.slice(0, 80).replace(/\n/g, ' ') + (sql.length > 80 ? '…' : '') : '—'
                const isExpanded = expandedSqlKey === qid
                return (
                  <tr key={qid} style={{ borderTop: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.625rem 0.75rem' }}>Query {qid}</td>
                    <td style={{ padding: '0.625rem 0.75rem' }}>{String((t as Record<string, unknown>).question ?? (t as Record<string, unknown>).title ?? '').slice(0, 60)}</td>
                    <td
                      style={{ ...SQL_CELL_STYLE, whiteSpace: isExpanded ? 'pre-wrap' : 'nowrap', maxWidth: isExpanded ? 'none' : 200, cursor: sql ? 'pointer' : 'default' }}
                      title={sql ? 'Click to expand/collapse' : undefined}
                      onClick={() => sql && setExpandedSqlKey(isExpanded ? null : qid)}
                    >
                      {isExpanded ? sql : sqlPreview}
                    </td>
                    <td style={{ padding: '0.625rem 0.75rem' }}>{String((t as Record<string, unknown>).task_status || 'Completed')}</td>
                    <td style={{ padding: '0.625rem 0.75rem' }}>{String((t as Record<string, unknown>).audit_status || 'Ready to Audit')}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        </>
      )}
      {!loading && tasks.length === 0 && source && (
        <p style={{ color: 'var(--fg-muted)', fontSize: '0.875rem' }}>
          No tasks found for {source}. Try another database.
        </p>
      )}
      <SchemaView source={source} />
      <ToolsSection source={source} />
    </div>
  )
}
