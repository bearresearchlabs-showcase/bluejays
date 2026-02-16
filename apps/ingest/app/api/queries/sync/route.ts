import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { parseQueriesMd, formatQueriesMd } from '@/lib/queries-convert'
import { writeFileSync, existsSync, mkdirSync } from 'fs'
import { join } from 'path'

/**
 * POST /api/queries/sync
 * Sync queries between md and json. Annotator and staff only (customer cannot edit).
 */
export async function POST(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  if (session.user === 'customer') {
    return NextResponse.json({ error: 'Forbidden: customers cannot edit queries' }, { status: 403 })
  }

  let body: { source: string; format: 'json' | 'md'; content: unknown }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  }

  const { source, format, content } = body
  if (!source || !format || content === undefined) {
    return NextResponse.json({ error: 'source, format, and content required' }, { status: 400 })
  }

  const root = process.cwd()
  const isTemplate = source.toLowerCase() === 'template'
  const baseDir = isTemplate
    ? join(root, 'template')
    : join(root, 'source', source, 'app', 'QUERIES')

  const mdPath = join(baseDir, 'queries.md')
  const jsonPath = join(baseDir, 'queries.json')

  try {
    if (format === 'md') {
      const md = typeof content === 'string' ? content : String(content)
      const { queries } = parseQueriesMd(md)
      if (queries.length === 0) {
        return NextResponse.json({ error: 'No queries extracted from markdown' }, { status: 400 })
      }
      if (!existsSync(baseDir)) mkdirSync(baseDir, { recursive: true })
      const jsonContent = JSON.stringify(queries, null, 2)
      writeFileSync(jsonPath, jsonContent, 'utf-8')
      return NextResponse.json({
        status: 'success',
        source,
        format: 'md→json',
        queries_count: queries.length,
        written: [jsonPath],
      })
    }

    if (format === 'json') {
      const queries = Array.isArray(content)
        ? content
        : (content as { queries?: unknown[] })?.queries ?? []
      if (queries.length === 0) {
        return NextResponse.json({ error: 'No queries in content' }, { status: 400 })
      }
      if (!existsSync(baseDir)) mkdirSync(baseDir, { recursive: true })
      const jsonContent = JSON.stringify(queries, null, 2)
      writeFileSync(jsonPath, jsonContent, 'utf-8')
      const md = formatQueriesMd(queries as { db_id?: string; [key: string]: unknown }[], {
        db_id: isTemplate ? 'healthcare_hospital' : source,
        db_name: `${source} — Query Documentation`,
      })
      writeFileSync(mdPath, md, 'utf-8')
      return NextResponse.json({
        status: 'success',
        source,
        format: 'json→md+json',
        queries_count: queries.length,
        written: [jsonPath, mdPath],
      })
    }

    return NextResponse.json({ error: 'format must be json or md' }, { status: 400 })
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 })
  }
}
