'use client'

/**
 * Task pipeline visualization aligned with Scale's Rapid pipelines:
 * https://scale.com/docs/rapid-or-pipelines
 * Phases: Attempt (attempter) → Review (reviewer) → Complete | Rejected
 */
import { useEffect, useState } from 'react'

type Phase = 'attempt' | 'review' | 'complete' | 'rejected'

const PHASES: { id: Phase; label: string; color: string }[] = [
  { id: 'attempt', label: 'Attempt', color: 'var(--accent)' },
  { id: 'review', label: 'Review', color: '#f59e0b' },
  { id: 'complete', label: 'Complete', color: '#10b981' },
  { id: 'rejected', label: 'Rejected', color: '#ef4444' },
]

function getPhase(task: Record<string, unknown>): Phase {
  const ts = String(task.task_status ?? '').toLowerCase()
  const as = String(task.audit_status ?? '').toLowerCase()
  if (as.includes('reject')) return 'rejected'
  if (as.includes('approv') || ts.includes('complet') || as.includes('approved')) return 'complete'
  if (as.includes('review') || as.includes('audit') || ts.includes('review')) return 'review'
  return 'attempt'
}

function Chip({ phase, label }: { phase: Phase; label: string }) {
  const p = PHASES.find((x) => x.id === phase)
  const color = p?.color ?? 'var(--fg-muted)'
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '0.2rem 0.5rem',
        fontSize: '0.6875rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        background: `${color}22`,
        color,
        borderRadius: 4,
        border: `1px solid ${color}44`,
      }}
    >
      {label}
    </span>
  )
}

export function TaskPipeline({ source: initialSource }: { source?: string }) {
  const [sources, setSources] = useState<string[]>([])
  const [source, setSource] = useState(initialSource || '')
  const [tasks, setTasks] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(false)

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

  const byPhase = PHASES.reduce((acc, p) => {
    acc[p.id] = tasks.filter((t) => getPhase(t as Record<string, unknown>) === p.id)
    return acc
  }, {} as Record<Phase, Record<string, unknown>[]>)

  return (
    <div>
      <section style={{ marginBottom: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h2 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>
          Pipeline — Scale-style staging
        </h2>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '1rem' }}>
          Tasks flow: Attempt → Review → Complete or Rejected. See{' '}
          <a href="https://scale.com/docs/rapid-or-pipelines" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>
            Scale Rapid Pipelines
          </a>
        </p>
        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>
          Database
        </label>
        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          style={{ padding: '0.5rem 0.875rem', minWidth: 160, background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--fg)', borderRadius: 6, fontSize: '0.875rem' }}
        >
          {sources.map((s) => (
            <option key={s} value={s}>{s === 'template' ? 'template' : s}</option>
          ))}
        </select>
      </section>

      {loading && <p style={{ color: 'var(--fg-muted)', fontSize: '0.875rem' }}>Loading…</p>}

      {!loading && (
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${PHASES.length}, minmax(200px, 1fr))`, gap: '1rem', overflowX: 'auto', minHeight: 400 }}>
          {PHASES.map((p) => (
            <div
              key={p.id}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                padding: '0.75rem',
                minWidth: 200,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border)' }}>
                <span style={{ width: 8, height: 8, borderRadius: 4, background: p.color }} />
                <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--fg)' }}>{p.label}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--fg-muted)', marginLeft: 'auto' }}>
                  {byPhase[p.id]?.length ?? 0}
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {(byPhase[p.id] ?? []).map((t, i) => {
                  const q = t as Record<string, unknown>
                  const title = String(q.question ?? q.title ?? `Query ${q.question_id ?? q.number ?? i + 1}`).slice(0, 50)
                  const phase = getPhase(q)
                  return (
                    <div
                      key={i}
                      style={{
                        padding: '0.5rem 0.625rem',
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 6,
                        fontSize: '0.8125rem',
                      }}
                    >
                      <div style={{ marginBottom: '0.25rem', fontWeight: 500 }}>{title}{title.length >= 50 ? '…' : ''}</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', alignItems: 'center' }}>
                        <Chip phase={phase} label={PHASES.find((x) => x.id === phase)?.label ?? phase} />
                        {q.difficulty != null && (
                          <span style={{ fontSize: '0.6875rem', color: 'var(--fg-muted)' }}>
                            {String(q.difficulty)}
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
