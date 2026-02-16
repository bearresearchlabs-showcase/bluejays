import { ViewSelector } from '@/components/ViewSelector'
import { SchemaViewWrapper } from '@/components/SchemaViewWrapper'
import { LiveSQLBenchIngestForm } from '@/components/LiveSQLBenchIngestForm'
import Link from 'next/link'

export default function DashboardPage() {
  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '2rem' }}>
        <Link href="/" style={{ marginRight: '1rem' }}>Annotator</Link>
        <Link href="/suite" style={{ marginRight: '1rem' }}>Databases</Link>
        <Link href="/customer" style={{ marginRight: '1rem' }}>Customer Portal</Link>
        <Link href="/admin/tasks" style={{ marginRight: '1rem' }}>Task Board</Link>
        <Link href="/admin/privileges" style={{ marginRight: '1rem' }}>Privileges</Link>
        <Link href="/validate" style={{ marginRight: '1rem' }}>Validate</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Dashboard</h1>
      <p style={{ color: 'var(--fg-muted)', fontSize: '0.9rem', marginBottom: '2rem' }}>
        SQL annotation workbench — hub for annotator, task board, and database suite
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
        <Link
          href="/"
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
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Annotator</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>
            Load queries, annotate SQL, validate against live databases.
          </p>
        </Link>
        <Link
          href="/admin/tasks"
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
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Task Board</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>
            30 independent task submissions. Accept/Fix/Reject workflow.
          </p>
        </Link>
        <Link
          href="/suite"
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
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Databases</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>
            Browse db-1 through db-16. Jump to Customer Portal per database.
          </p>
        </Link>
        <Link
          href="/customer"
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
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Customer Portal</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>
            Scale-style customer view: task filters, visualizations, export.
          </p>
        </Link>
      </div>
      <div style={{ marginTop: '2rem', maxWidth: 640 }}>
        <LiveSQLBenchIngestForm />
      </div>
      <SchemaViewWrapper />
    </div>
  )
}
