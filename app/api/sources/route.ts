import { NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { discoverSources, getDataRoot } from '@/lib/data'
import { existsSync } from 'fs'
import { join } from 'path'

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const sources = discoverSources()
  // #region agent log
  const cwd = process.cwd()
  const dataRoot = getDataRoot()
  const srcExists = existsSync(join(dataRoot, 'source'))
  const tplExists = existsSync(join(dataRoot, 'template'))
  const logPayload = { location: 'api/sources/route.ts:GET', message: 'API sources invoked', data: { cwd, dataRoot, sources, srcExists, tplExists, hypothesisId: 'H2' }, timestamp: Date.now() }
  console.log('[DEBUG]', JSON.stringify(logPayload))
  try {
    await fetch('http://127.0.0.1:7242/ingest/ede760b6-b9c4-4904-b4d5-a8169c1a50e4', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(logPayload) }).catch(() => {})
  } catch {}
  // #endregion
  return NextResponse.json({ sources })
}
