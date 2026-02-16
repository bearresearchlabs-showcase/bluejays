'use client'

import { useEffect, useState } from 'react'

type QueryRecord = Record<string, unknown>

function isFieldDefs(q: QueryRecord): boolean {
  return q && typeof q === 'object' && '_field_definitions' in q && Object.keys(q).length <= 2
}

export function AnnotatorWorkbench() {
  const [sources, setSources] = useState<string[]>([])
  const [source, setSource] = useState('')
  const [queries, setQueries] = useState<QueryRecord[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'ok' | 'err'; text: string } | null>(null)

  useEffect(() => {
    fetch('/api/sources')
      .then((r) => r.json())
      .then((d) => {
        const s = d.sources || ['template']
        setSources(s)
        setSource((prev) => (prev ? prev : s[0] || ''))
      })
      .catch(() => setSources(['template']))
  }, [])

  const [rawQueries, setRawQueries] = useState<QueryRecord[]>([])

  useEffect(() => {
    if (!source) return
    setLoading(true)
    setSelectedIndex(null)
    fetch(`/api/queries?source=${encodeURIComponent(source)}`)
      .then((r) => r.json())
      .then((d) => {
        const raw = (d.queries || []) as QueryRecord[]
        setRawQueries(raw)
        setQueries(raw.filter((q) => !isFieldDefs(q)))
        setLoading(false)
      })
      .catch(() => {
        setQueries([])
        setLoading(false)
      })
  }, [source])

  const selected = selectedIndex !== null ? queries[selectedIndex] : null

  const handleSave = async () => {
    if (!source || selectedIndex === null) return
    setSaving(true)
    setMessage(null)
    try {
      const editableIndices = rawQueries.map((q, i) => (isFieldDefs(q) ? -1 : i)).filter((i) => i >= 0)
      const actualIndex = editableIndices[selectedIndex]
      if (actualIndex === undefined) throw new Error('Invalid selection')
      const updated = [...rawQueries]
      updated[actualIndex] = { ...selected }
      const res = await fetch('/api/queries/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, format: 'json', content: updated }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Save failed')
      setRawQueries(updated)
      setQueries(updated.filter((q) => !isFieldDefs(q)))
      setMessage({ type: 'ok', text: `Saved ${data.queries_count} queries` })
    } catch (e) {
      setMessage({ type: 'err', text: String(e) })
    } finally {
      setSaving(false)
    }
  }

  const updateField = (key: string, value: unknown) => {
    if (selectedIndex === null || !selected) return
    const next = { ...selected, [key]: value }
    setQueries((prev) => {
      const copy = [...prev]
      copy[selectedIndex] = next
      return copy
    })
  }

  const questionKey = selected && 'question' in selected ? 'question' : 'title'
  const sqlKey = selected && 'SQL' in selected ? 'SQL' : 'sql'
  const evidenceKey = selected && 'evidence' in selected ? 'evidence' : 'description'

  const question = selected ? String(selected.question ?? selected.title ?? '') : ''
  const sql = selected ? String(selected.SQL ?? selected.sql ?? '') : ''
  const evidence = selected ? String(selected.evidence ?? selected.description ?? '') : ''
  const difficulty = selected ? String(selected.difficulty ?? 'moderate') : 'moderate'

  return (
    <div>
      <section style={{ marginBottom: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h2 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Select database to annotate</h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div>
            <label htmlFor="ann-db" style={{ display: 'block', fontSize: '0.75rem', color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>
              Database
            </label>
            <select
              id="ann-db"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              style={{ padding: '0.5rem 0.875rem', minWidth: 140, background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--fg)', borderRadius: 6, fontSize: '0.875rem' }}
            >
              {sources.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {loading && <p style={{ color: 'var(--fg-muted)' }}>Loading…</p>}

      {!loading && queries.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: '1rem', minHeight: 400 }}>
          <div style={{ border: '1px solid var(--border)', borderRadius: 8, overflow: 'auto', maxHeight: 500 }}>
            {queries.map((q, i) => {
              const title = String(q.question ?? q.title ?? `Query ${q.question_id ?? q.number ?? i + 1}`).slice(0, 50)
              const active = i === selectedIndex
              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => setSelectedIndex(i)}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    textAlign: 'left',
                    background: active ? 'var(--accent)' : 'transparent',
                    color: active ? '#fff' : 'var(--fg)',
                    border: 'none',
                    borderBottom: '1px solid var(--border)',
                    cursor: 'pointer',
                    fontSize: '0.8125rem',
                  }}
                >
                  {`${q.question_id ?? q.number ?? i + 1}. ${title}${title.length >= 50 ? '…' : ''}`}
                </button>
              )
            })}
          </div>

          <div style={{ border: '1px solid var(--border)', borderRadius: 8, padding: '1rem', overflow: 'auto' }}>
            {selected ? (
              <>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>Question (natural language)</label>
                  <textarea
                    value={question}
                    onChange={(e) => updateField(questionKey, e.target.value)}
                    rows={2}
                    style={{ width: '100%', padding: '0.5rem', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 6, fontSize: '0.875rem', fontFamily: 'inherit' }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>SQL</label>
                  <textarea
                    value={sql}
                    onChange={(e) => updateField(sqlKey, e.target.value)}
                    rows={10}
                    style={{ width: '100%', padding: '0.5rem', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 6, fontSize: '0.8125rem', fontFamily: 'monospace' }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>Evidence / reasoning</label>
                  <textarea
                    value={evidence}
                    onChange={(e) => updateField(evidenceKey, e.target.value)}
                    rows={3}
                    style={{ width: '100%', padding: '0.5rem', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 6, fontSize: '0.875rem', fontFamily: 'inherit' }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => updateField('difficulty', e.target.value)}
                    style={{ padding: '0.5rem', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 6, fontSize: '0.875rem' }}
                  >
                    <option value="simple">simple</option>
                    <option value="moderate">moderate</option>
                    <option value="challenging">challenging</option>
                  </select>
                </div>
                {message && (
                  <p style={{ color: message.type === 'ok' ? 'var(--accent)' : 'var(--error)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    {message.text}
                  </p>
                )}
                <button
                  onClick={handleSave}
                  disabled={saving}
                  style={{ padding: '0.5rem 1rem', background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 6, fontSize: '0.875rem', cursor: saving ? 'not-allowed' : 'pointer', fontWeight: 500 }}
                >
                  {saving ? 'Saving…' : 'Save changes'}
                </button>
              </>
            ) : (
              <p style={{ color: 'var(--fg-muted)' }}>Select a query from the list to annotate.</p>
            )}
          </div>
        </div>
      )}

      {!loading && queries.length === 0 && source && (
        <p style={{ color: 'var(--fg-muted)' }}>No queries found for {source}.</p>
      )}
    </div>
  )
}
