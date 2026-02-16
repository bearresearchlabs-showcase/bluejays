'use client'

import { useState } from 'react'

export function LiveSQLBenchIngestForm() {
  const [input, setInput] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')
    setResult(null)
    try {
      let parsed: unknown
      try {
        parsed = JSON.parse(input)
      } catch {
        setStatus('error')
        setResult({ error: 'Invalid JSON' })
        return
      }
      const res = await fetch('/api/ingest/livesqlbench', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed),
      })
      const data = await res.json()
      if (!res.ok) {
        setStatus('error')
        setResult(data)
        return
      }
      setStatus('success')
      setResult(data)
    } catch (err) {
      setStatus('error')
      setResult({ error: String(err) })
    }
  }

  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1.25rem' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>LiveSQLBench Ingest</h3>
      <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '1rem' }}>
        Paste LiveSQLBench JSON (single instance or array) from{' '}
        <a href="https://huggingface.co/datasets/birdsql/livesqlbench-base-lite" target="_blank" rel="noreferrer">
          birdsql/livesqlbench-base-lite
        </a>{' '}
        or full-v1.
      </p>
      <form onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder='[{"instance_id":"alien_1","selected_database":"alien","query":"...","category":"Query",...}]'
          rows={6}
          style={{
            width: '100%',
            padding: '0.75rem',
            fontFamily: 'monospace',
            fontSize: '0.8125rem',
            borderRadius: 6,
            border: '1px solid var(--border)',
            background: 'var(--bg)',
            color: 'var(--fg)',
          }}
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          style={{
            marginTop: '0.75rem',
            padding: '0.5rem 1rem',
            borderRadius: 6,
            border: '1px solid var(--border)',
            background: 'var(--bg)',
            color: 'var(--fg)',
            cursor: status === 'loading' ? 'not-allowed' : 'pointer',
          }}
        >
          {status === 'loading' ? 'Ingesting…' : 'Ingest'}
        </button>
      </form>
      {result && (
        <pre
          data-testid="livesqlbench-result"
          style={{
            marginTop: '1rem',
            padding: '0.75rem',
            fontSize: '0.75rem',
            background: 'var(--bg)',
            borderRadius: 6,
            overflow: 'auto',
            maxHeight: 200,
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  )
}
