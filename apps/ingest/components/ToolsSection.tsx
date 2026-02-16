'use client'

import { DbDiagramEmbed } from './DbDiagramEmbed'
import { ChartDBEmbed } from './ChartDBEmbed'
import { LiamEmbed } from './LiamEmbed'

export function ToolsSection({ source }: { source: string }) {
  return (
    <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
      <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--fg)' }}>Tools</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <DbDiagramEmbed source={source} />
        <ChartDBEmbed source={source} />
        <LiamEmbed source={source} />
      </div>
    </section>
  )
}
