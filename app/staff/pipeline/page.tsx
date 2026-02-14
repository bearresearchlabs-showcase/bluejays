import { ViewSelector } from '@/components/ViewSelector'
import { TaskPipeline } from '@/components/TaskPipeline'
import Link from 'next/link'

export default function StaffPipelinePage() {
  return (
    <div className="container">
      <ViewSelector />
      <nav style={{ marginBottom: '1.5rem' }}>
        <Link href="/staff" style={{ marginRight: '1rem' }}>Staff</Link>
        <Link href="/staff/pipeline" style={{ marginRight: '1rem' }}>Pipeline</Link>
        <Link href="/admin/tasks" style={{ marginRight: '1rem' }}>Task Board</Link>
        <Link href="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/admin/privileges" style={{ marginRight: '1rem' }}>Privileges</Link>
        <Link href="/logout">Log out</Link>
      </nav>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>
        Task Pipeline
      </h1>
      <p style={{ color: 'var(--fg-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
        Scale-style visualization: Attempt → Review → Complete or Rejected. Chiplet tags show staging phase.
      </p>
      <TaskPipeline />
    </div>
  )
}
