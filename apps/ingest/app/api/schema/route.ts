import { NextRequest, NextResponse } from 'next/server'
import { loadSchema } from '@/lib/data'

export async function GET(request: NextRequest) {
  const source = request.nextUrl.searchParams.get('source')
  if (!source) {
    return NextResponse.json({ error: 'source required' }, { status: 400 })
  }
  const { schema, error } = loadSchema(source)
  if (error) {
    return NextResponse.json({ error }, { status: 404 })
  }
  return NextResponse.json({ schema, source })
}
