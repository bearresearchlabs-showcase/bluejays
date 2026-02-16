'use client'

import { useEffect, useState } from 'react'

/**
 * Embeds dbdiagram.io ER diagram with schema pre-loaded.
 * Fetches DBML from /api/schema/dbml and encodes for dbdiagram.io/embed?c=
 */
export function DbDiagramEmbed({ source }: { source: string }) {
  const [embedUrl, setEmbedUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const res = await fetch(`/api/schema/dbml?source=${encodeURIComponent(source)}`)
        if (!res.ok) {
          setError(res.status === 404 ? 'Schema not found' : 'Failed to load schema')
          return
        }
        const dbml = await res.text()
        if (cancelled) return
        // dbdiagram.io: Base64(UTF-8) then URL-encode
        const base64 = btoa(unescape(encodeURIComponent(dbml)))
        const c = encodeURIComponent(base64)
        setEmbedUrl(`https://dbdiagram.io/embed?c=${c}`)
      } catch (e) {
        if (!cancelled) setError(String(e))
      }
    }
    load()
    return () => { cancelled = true }
  }, [source])

  if (error) {
    return (
      <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>dbdiagram.io — {source}</h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>{error}</p>
      </section>
    )
  }

  if (!embedUrl) {
    return (
      <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>dbdiagram.io — {source}</h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)' }}>Loading schema…</p>
      </section>
    )
  }

  return (
    <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
      <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>dbdiagram.io — {source}</h3>
      <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '0.75rem' }}>
        Entity-Relationship diagram (schema embedded).
      </p>
      <iframe
        src={embedUrl}
        width="100%"
        height={420}
        style={{ border: 0, borderRadius: 6 }}
        loading="lazy"
        allowFullScreen
        title={`dbdiagram.io ER diagram for ${source}`}
      />
      <a
        href={embedUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{ display: 'inline-block', marginTop: '0.5rem', fontSize: '0.8125rem', color: 'var(--accent)' }}
      >
        Open in new tab →
      </a>
    </section>
  )
}
