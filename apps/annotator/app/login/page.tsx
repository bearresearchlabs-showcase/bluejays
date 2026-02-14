import { redirect } from 'next/navigation'
import { getSession } from '@/lib/auth'
import Link from 'next/link'

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ err?: string; from?: string }>
}) {
  const session = await getSession()
  if (session) {
    redirect(session.user === 'customer' ? '/customer' : '/')
  }

  const params = await searchParams
  const err = params.err
  const from = params.from

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '2rem',
          width: '100%',
          maxWidth: 360,
        }}
      >
        <h1 style={{ fontSize: '1.25rem', margin: '0 0 1.5rem 0' }}>SQL Annotator</h1>
        <form method="post" action="/api/login">
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.375rem', textTransform: 'uppercase' }}>
            Username
          </label>
          <input
            type="text"
            name="user"
            placeholder="staff, annotator, or customer"
            required
            autoComplete="username"
            style={{
              width: '100%',
              padding: '0.625rem 0.75rem',
              background: 'var(--bg)',
              border: '1px solid var(--border)',
              color: 'var(--fg)',
              borderRadius: 6,
              fontSize: '0.9375rem',
              marginBottom: '1rem',
            }}
          />
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg-muted)', marginBottom: '0.375rem', textTransform: 'uppercase' }}>
            Password
          </label>
          <input
            type="password"
            name="password"
            placeholder="••••••••"
            required
            autoComplete="current-password"
            style={{
              width: '100%',
              padding: '0.625rem 0.75rem',
              background: 'var(--bg)',
              border: '1px solid var(--border)',
              color: 'var(--fg)',
              borderRadius: 6,
              fontSize: '0.9375rem',
              marginBottom: '1rem',
            }}
          />
          <div style={{ marginBottom: '1rem' }}>
            <input type="checkbox" name="stay" id="stay" value="1" defaultChecked />
            <label htmlFor="stay" style={{ marginLeft: '0.5rem', fontSize: '0.875rem', fontWeight: 400 }}>
              Stay logged in (30 days)
            </label>
          </div>
          <button
            type="submit"
            style={{
              width: '100%',
              padding: '0.75rem',
              background: 'var(--accent)',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              fontSize: '0.9375rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Log in
          </button>
          {err && (
            <p style={{ color: 'var(--error)', fontSize: '0.875rem', marginTop: '0.5rem' }}>{err.replace(/\+/g, ' ')}</p>
          )}
        </form>
      </div>
    </div>
  )
}
