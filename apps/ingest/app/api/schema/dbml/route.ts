import { NextRequest, NextResponse } from 'next/server'
import { loadSchema } from '@/lib/data'
import { schemaToDbml } from '@/lib/schema-to-dbml'

export async function GET(request: NextRequest) {
  const source = request.nextUrl.searchParams.get('source')
  if (!source) {
    return NextResponse.json({ error: 'source required' }, { status: 400 })
  }
  const { schema, error } = loadSchema(source)
  if (error) {
    return NextResponse.json({ error }, { status: 404 })
  }
  const dbml = schemaToDbml(schema)
  return new NextResponse(dbml, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  })
}
