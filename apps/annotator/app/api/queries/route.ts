import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { loadQueries } from '@/lib/data'

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const source = request.nextUrl.searchParams.get('source')
  if (!source) {
    return NextResponse.json({ error: 'source required' }, { status: 400 })
  }
  const { queries, error } = loadQueries(source)
  if (error) {
    return NextResponse.json({ error }, { status: 404 })
  }
  return NextResponse.json({ queries })
}
