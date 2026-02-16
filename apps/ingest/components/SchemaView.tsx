'use client'

import { useEffect, useState } from 'react'
import { SqlCodeBlock } from './SqlCodeBlock'

export function SchemaView({ source }: { source: string }) {
  const [schema, setSchema] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!source) return
    let cancelled = false
    const run = async () => {
      const res = await fetch(`/api/schema?source=${encodeURIComponent(source)}`)
      const d = await res.json()
      if (cancelled) return
      if (d.error) {
        setError(d.error)
        setSchema(null)
      } else {
        setSchema(d.schema || '')
        setError(null)
      }
      setLoading(false)
    }
    run().catch((e) => {
      if (!cancelled) {
        setError(String(e))
        setSchema(null)
        setLoading(false)
      }
    })
    queueMicrotask(() => {
      if (!cancelled) {
        setLoading(true)
        setError(null)
      }
    })
    return () => { cancelled = true }
  }, [source])

  const displaySchema = source ? schema : null
  const displayError = source ? error : null
  const displayLoading = source ? loading : false

  const handleCopy = () => {
    if (!displaySchema) return
    navigator.clipboard.writeText(displaySchema).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  if (!source) {
    return (
      <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>Schema</h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>Select a database to view its schema.</p>
      </section>
    )
  }

  if (displayLoading) {
    return (
      <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>Schema — {source}</h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>Loading…</p>
      </section>
    )
  }

  if (displayError) {
    return (
      <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>Schema — {source}</h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>{displayError}</p>
      </section>
    )
  }

  return (
    <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, margin: 0, color: 'var(--fg)' }}>Schema — {source}</h3>
        <button
          type="button"
          onClick={handleCopy}
          style={{
            fontSize: '0.75rem',
            padding: '0.25rem 0.5rem',
            background: 'var(--bg)',
            border: '1px solid var(--border)',
            borderRadius: 4,
            cursor: 'pointer',
            color: 'var(--fg)',
          }}
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <SqlCodeBlock sql={displaySchema ?? ''} />
    </section>
  )
}
