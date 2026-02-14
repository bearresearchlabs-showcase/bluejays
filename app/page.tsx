import { ViewSelector } from '@/components/ViewSelector'
import Link from 'next/link'

export default function AnnotatorPage() {
  return (
    <div className="container">
      <ViewSelector />
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0 }}>SQL Annotator</h1>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginTop: '0.25rem' }}>
          <Link href="/dashboard">Dashboard</Link> · <Link href="/suite">Full Suite</Link> ·{' '}
          <Link href="/customer">Customer Portal</Link> · <Link href="/logout">Log out</Link>
        </p>
      </div>
      <p style={{ color: 'var(--fg-muted)' }}>
        Annotator workbench — load queries, annotate SQL, validate. Use the Python app for full functionality.
      </p>
      <p style={{ marginTop: '1rem', fontSize: '0.875rem' }}>
        <Link href="/dashboard">Go to Dashboard</Link> for all views.
      </p>
    </div>
  )
}
