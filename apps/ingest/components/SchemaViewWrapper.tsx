'use client'

import { useEffect, useState } from 'react'
import { SchemaView } from './SchemaView'
import { ToolsSection } from './ToolsSection'

export function SchemaViewWrapper() {
  const [sources, setSources] = useState<string[]>([])
  const [source, setSource] = useState('')

  useEffect(() => {
    fetch('/api/sources')
      .then((r) => r.json())
      .then((d) => {
        const s = d.sources || ['template']
        setSources(s)
        setSource((prev) => prev || (s.find((x: string) => x.startsWith('db-')) || s[0]))
      })
      .catch(() => setSources(['template']))
  }, [])

  return (
    <div style={{ marginTop: '2rem' }}>
      {sources.length > 1 && (
        <div style={{ marginBottom: '0.75rem' }}>
          <label htmlFor="schema-db-select" style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.25rem' }}>
            Database
          </label>
          <select
            id="schema-db-select"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', minWidth: 120, background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--fg)', borderRadius: 6, fontSize: '0.875rem' }}
          >
            {sources.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      )}
      <SchemaView source={source} />
      <ToolsSection source={source} />
    </div>
  )
}
