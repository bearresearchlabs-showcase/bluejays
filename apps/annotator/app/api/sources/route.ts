import { NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { discoverSources } from '@/lib/data'
import { join } from 'path'

export async function GET() {
  // #region agent log
  const cwd = process.cwd()
  const root = join(cwd, '..', '..')
  const srcDir = join(root, 'source')
  try {
    await fetch('http://127.0.0.1:7242/ingest/ede760b6-b9c4-4904-b4d5-a8169c1a50e4', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'api/sources/route.ts:GET',
        message: 'API sources invoked',
        data: { cwd, root, srcDir, hypothesisId: 'H2' },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
  } catch {}
  // #endregion
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const sources = discoverSources()
  return NextResponse.json({ sources })
}
