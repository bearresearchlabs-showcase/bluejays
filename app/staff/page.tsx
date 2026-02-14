import { ViewSelector } from '@/components/ViewSelector'
import Link from 'next/link'

export default function StaffPage() {
  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '2rem' }}>
        <Link href="/" style={{ marginRight: '1rem' }}>Annotator</Link>
        <Link href="/staff/pipeline" style={{ marginRight: '1rem' }}>Pipeline</Link>
        <Link href="/admin/tasks" style={{ marginRight: '1rem' }}>Task Board</Link>
        <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/customer" style={{ marginRight: '1rem' }}>Customer Portal</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Staff</h1>
      <p style={{ color: 'var(--fg-muted)', fontSize: '0.9rem', marginBottom: '2rem' }}>
        Internal tools for annotators — workbench, task board, and pipeline
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
        <Link href="/" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1.25rem', textDecoration: 'none', color: 'inherit', display: 'block' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Annotator</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>Load queries, annotate SQL, validate.</p>
        </Link>
        <Link href="/staff/pipeline" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1.25rem', textDecoration: 'none', color: 'inherit', display: 'block' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Pipeline</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>Scale-style staging: Attempt → Review → Complete.</p>
        </Link>
        <Link href="/admin/tasks" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1.25rem', textDecoration: 'none', color: 'inherit', display: 'block' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Task Board</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>30 independent task submissions.</p>
        </Link>
        <Link href="/dashboard" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '1.25rem', textDecoration: 'none', color: 'inherit', display: 'block' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem 0' }}>Dashboard</h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', margin: 0 }}>Full hub — all views.</p>
        </Link>
      </div>
    </div>
  )
}
