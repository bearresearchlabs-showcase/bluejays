import { redirect } from 'next/navigation'
import { getSession } from '@/lib/auth'

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

  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-[var(--bg)]">
      <div className="w-full max-w-[360px] p-8 rounded-lg border border-[var(--border)] bg-[var(--bg-card)]">
        <h1 className="text-xl font-semibold mb-6 text-[var(--fg)]">SQL Annotator</h1>
        <form method="post" action="/api/login">
          <label htmlFor="user" className="block text-xs font-semibold mb-1.5 uppercase text-[var(--fg-muted)]">
            Username
          </label>
          <input
            id="user"
            type="text"
            name="user"
            placeholder="staff, annotator, or customer"
            required
            autoComplete="username"
            className="w-full px-3 py-2.5 mb-4 rounded-md text-[15px] bg-[var(--bg)] border border-[var(--border)] text-[var(--fg)] placeholder:text-[var(--fg-muted)]"
          />
          <label htmlFor="password" className="block text-xs font-semibold mb-1.5 uppercase text-[var(--fg-muted)]">
            Password
          </label>
          <input
            id="password"
            type="password"
            name="password"
            placeholder="••••••••"
            required
            autoComplete="current-password"
            className="w-full px-3 py-2.5 mb-4 rounded-md text-[15px] bg-[var(--bg)] border border-[var(--border)] text-[var(--fg)] placeholder:text-[var(--fg-muted)]"
          />
          <div className="mb-4 flex items-center gap-2">
            <input type="checkbox" name="stay" id="stay" value="1" defaultChecked className="rounded" />
            <label htmlFor="stay" className="text-sm text-[var(--fg)]">
              Stay logged in (30 days)
            </label>
          </div>
          <button
            type="submit"
            className="w-full py-3 rounded-md text-[15px] font-semibold cursor-pointer bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)]"
          >
            Log in
          </button>
          {err && (
            <p className="mt-2 text-sm text-[var(--error)]">{err.replace(/\+/g, ' ')}</p>
          )}
        </form>
      </div>
    </div>
  )
}
