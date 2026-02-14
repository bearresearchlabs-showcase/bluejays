import { NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { discoverSources } from '@/lib/data'

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const sources = discoverSources()
  return NextResponse.json({ sources })
}
