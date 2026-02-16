'use client'

/**
 * Liam ERD: https://liambx.com
 * For public GitHub repos: https://liambx.com/erd/p/github.com/org/repo/blob/branch/path/to/schema.sql
 * Requires NEXT_PUBLIC_GITHUB_REPO (e.g. "org/repo") and optionally NEXT_PUBLIC_GITHUB_BRANCH (default: main).
 */
export function LiamEmbed({ source }: { source: string }) {
  const repo = process.env.NEXT_PUBLIC_GITHUB_REPO?.trim()
  const branch = process.env.NEXT_PUBLIC_GITHUB_BRANCH?.trim() || 'main'

  // Build path: source/db-N/app/DATABASE/schema.sql (primary) or source/db-N/data/schema.sql
  const n = source.replace(/^db-?/i, '').trim()
  const num = parseInt(n, 10)
  const dbSlug = isNaN(num) ? source : `db-${num}`
  const schemaPath = `source/${dbSlug}/app/DATABASE/schema.sql`

  const repoSlug = repo?.replace(/^https?:\/\/github\.com\/?/, '').replace(/\/$/, '')
  const liamUrl = repoSlug
    ? `https://liambx.com/erd/p/github.com/${repoSlug}/blob/${branch}/${schemaPath}`
    : null

  if (!liamUrl) {
    return (
      <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>Liam ERD — {source}</h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '0.5rem' }}>
          Set <code style={{ fontSize: '0.75rem' }}>NEXT_PUBLIC_GITHUB_REPO</code> (e.g. &quot;org/repo&quot;) to link to your schema on GitHub.
        </p>
        <a
          href="https://liambx.com"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'inline-block',
            padding: '0.5rem 1rem',
            background: 'var(--accent)',
            color: '#fff',
            borderRadius: 6,
            fontSize: '0.875rem',
            textDecoration: 'none',
            fontWeight: 500,
          }}
        >
          Open Liam ERD →
        </a>
      </section>
    )
  }

  return (
    <section style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}>
      <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>Liam ERD — {source}</h3>
      <p style={{ fontSize: '0.8125rem', color: 'var(--fg-muted)', marginBottom: '0.75rem' }}>
        Entity-Relationship diagram from schema on GitHub.
      </p>
      <a
        href={liamUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: 'inline-block',
          padding: '0.5rem 1rem',
          background: 'var(--accent)',
          color: '#fff',
          borderRadius: 6,
          fontSize: '0.875rem',
          textDecoration: 'none',
          fontWeight: 500,
        }}
      >
        Open Liam ERD →
      </a>
    </section>
  )
}
