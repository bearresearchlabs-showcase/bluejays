import { ViewSelector } from '@/components/ViewSelector'
import Link from 'next/link'
import { CustomerPortal } from './CustomerPortal'

export default async function CustomerPage({
  searchParams,
}: {
  searchParams: Promise<{ source?: string }>
}) {
  const params = await searchParams
  const source = params.source

  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '2rem' }}>
        <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/suite" style={{ marginRight: '1rem' }}>Full Suite</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Customer Portal</h1>
      <p style={{ color: 'var(--fg-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
        Task overview, visualizations, and export — Scale-style customer view
      </p>
      <CustomerPortal defaultSource={source} />
    </div>
  )
}
