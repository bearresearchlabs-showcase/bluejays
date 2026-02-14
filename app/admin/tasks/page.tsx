import { ViewSelector } from '@/components/ViewSelector'
import Link from 'next/link'

export default function TaskBoardPage() {
  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '1.5rem' }}>
        <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/" style={{ marginRight: '1rem' }}>Annotator</Link>
        <Link href="/suite" style={{ marginRight: '1rem' }}>Full Suite</Link>
        <Link href="/customer" style={{ marginRight: '1rem' }}>Customer Portal</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0 }}>Task Board — 30 Queries</h1>
      <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginTop: '0.25rem' }}>
        Independent task submissions, Accept/Fix/Reject
      </p>
      <p style={{ marginTop: '1.5rem', color: 'var(--fg-muted)' }}>
        Use the Python annotator app for full task board functionality.
      </p>
    </div>
  )
}
