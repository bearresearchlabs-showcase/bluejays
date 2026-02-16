import { ViewSelector } from '@/components/ViewSelector'
import { SchemaViewWrapper } from '@/components/SchemaViewWrapper'
import Link from 'next/link'
import { discoverSources } from '@/lib/data'

const DB_NAMES: Record<string, string> = {
  'db-1': 'Chat Messaging',
  'db-2': 'Filling Station Retail',
  'db-3': 'Hierarchical Orders',
  'db-4': 'SharedAI Models',
  'db-5': 'POS Retail',
  'db-6': 'Weather Consulting',
  'db-7': 'Maritime Shipping',
  'db-8': 'Job Market',
  'db-9': 'Shipping Intelligence',
  'db-10': 'Marketing Intelligence',
  'db-11': 'Parking Intelligence',
  'db-12': 'Credit Card & Rewards',
  'db-13': 'AI Benchmark',
  'db-14': 'Cloud Instance Cost',
  'db-15': 'Electricity & Solar',
  'db-16': 'Flood Risk',
  template: 'Template',
}

export default function SuitePage() {
  const sources = discoverSources().filter((s) => s !== 'template')
  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '2rem' }}>
        <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/" style={{ marginRight: '1rem' }}>Annotator</Link>
        <Link href="/admin/tasks" style={{ marginRight: '1rem' }}>Task Board</Link>
        <Link href="/customer" style={{ marginRight: '1rem' }}>Customer Portal</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Full Suite</h1>
      <p style={{ color: 'var(--fg-muted)', fontSize: '0.9rem', marginBottom: '2rem' }}>
        All databases with queries.json — production databases for annotation
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
        {sources.map((s) => (
          <Link
            key={s}
            href={`/customer?source=${encodeURIComponent(s)}`}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: '1.25rem',
              textDecoration: 'none',
              color: 'inherit',
              display: 'block',
            }}
          >
            <span style={{ display: 'inline-block', background: 'rgba(59,130,246,0.2)', color: 'var(--accent)', padding: '0.2rem 0.5rem', borderRadius: 4, fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              {s}
            </span>
            <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>{DB_NAMES[s] || s}</h2>
            <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>30 queries · PostgreSQL</p>
          </Link>
        ))}
        {sources.length === 0 && <p style={{ color: 'var(--fg-muted)' }}>No databases found</p>}
      </div>
      <SchemaViewWrapper />
    </div>
  )
}
