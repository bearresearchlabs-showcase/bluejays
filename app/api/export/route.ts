import { NextRequest, NextResponse } from 'next/server'
import { getSession, getViewMode } from '@/lib/auth'
import { loadQueries } from '@/lib/data'

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const viewMode = await getViewMode()
  if (session.user === 'annotator' || (session.user === 'staff' && viewMode === 'annotator')) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }
  if (session.user === 'customer') {
    // customer can export
  }

  const source = request.nextUrl.searchParams.get('source')
  const fmt = request.nextUrl.searchParams.get('format') || 'csv'
  if (!source) {
    return NextResponse.json({ error: 'source required' }, { status: 400 })
  }

  const { queries, error } = loadQueries(source)
  if (error) {
    return NextResponse.json({ error }, { status: 404 })
  }

  if (fmt === 'json') {
    return NextResponse.json(
      { queries },
      {
        headers: {
          'Content-Disposition': `attachment; filename="submissions_${source.replace('-', '_')}.json"`,
        },
      }
    )
  }

  if (fmt === 'csv') {
    const cols = [
      'question_id', 'db_id', 'question', 'SQL', 'evidence', 'difficulty',
      'query_category', 'tables_used', 'expected_output',
      'task_status', 'audit_status', 'created_at', 'updated_at',
    ]
    const escape = (s: string) => `"${String(s).replace(/"/g, '""')}"`
    const rows = queries.map((q) => {
      const tables = q.tables_used || []
      const tablesStr = Array.isArray(tables) ? tables.join(', ') : String(tables)
      return cols.map((c) => {
        const v = c === 'tables_used' ? tablesStr : (q[c] ?? '')
        return escape(String(v))
      }).join(',')
    })
    const csv = [cols.join(','), ...rows].join('\n')
    return new NextResponse(csv, {
      headers: {
        'Content-Type': 'text/csv',
        'Content-Disposition': `attachment; filename="submissions_${source.replace('-', '_')}.csv"`,
      },
    })
  }

  return NextResponse.json({ error: 'format must be csv or json' }, { status: 400 })
}
