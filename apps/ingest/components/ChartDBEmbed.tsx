'use client'

import { useEffect, useState } from 'react'

const CHARTDB_URL = 'https://app.chartdb.io'

/**
 * ChartDB: Provides DBML for import. ChartDB imports via File → Import → .dbml (paste).
 * Fetches DBML from API and offers copy-to-clipboard + link to ChartDB.
 */
export function ChartDBEmbed({ source }: { source: string }) {
  const [dbml, setDbml] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const res = await fetch(`/api/schema/dbml?source=${encodeURIComponent(source)}`)
        if (!res.ok) {
          setError(res.status === 404 ? 'Schema not found' : 'Failed to load schema')
          return
        }
        const text = await res.text()
        if (!cancelled) setDbml(text)
      } catch (e) {
        if (!cancelled) setError(String(e))
      }
    }
    load()
    return () => { cancelled = true }
  }, [source])

  const handleCopy = async () => {
    if (!dbml) return
    try {
      await navigator.clipboard.writeText(dbml)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setError('Copy failed')
    }
  }

  if (error) {
    return (
      <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>ChartDB — {source}</h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>{error}</p>
      </section>
    )
  }

  return (
    <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
      <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>ChartDB — {source}</h3>
      <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '0.75rem' }}>
        Import schema: Copy DBML below, open ChartDB, then File → Import → .dbml and paste.
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
        <button
          type="button"
          onClick={handleCopy}
          disabled={!dbml}
          style={{
            padding: '0.5rem 1rem',
            background: dbml ? 'var(--accent)' : 'var(--border)',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            fontSize: '0.875rem',
            fontWeight: 500,
            cursor: dbml ? 'pointer' : 'not-allowed',
          }}
        >
          {copied ? 'Copied!' : 'Copy DBML'}
        </button>
        <a
          href={CHARTDB_URL}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'inline-block',
            padding: '0.5rem 1rem',
            background: 'var(--accent)',
            color: '#fff',
            borderRadius: 6,
            fontSize: '0.875rem',
            textDecoration: 'none',
            fontWeight: 500,
          }}
        >
          Open ChartDB →
        </a>
      </div>
      {!dbml && (
        <p style={{ fontSize: '0.75rem', color: 'var(--fg-muted)', marginTop: '0.5rem' }}>Loading schema…</p>
      )}
    </section>
  )
}
