import { NextRequest, NextResponse } from 'next/server'
import { getSession, getActiveRole } from '@/lib/auth'
import { loadQueries } from '@/lib/data'
import { formatQueriesMd } from '@/lib/queries-convert'
import { loadPrivilegesConfig, canExport } from '@/lib/privileges'

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const activeRole = await getActiveRole()
  const config = loadPrivilegesConfig()
  if (!canExport(session.user, activeRole, config)) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
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

  if (fmt === 'md') {
    const md = formatQueriesMd(queries as { db_id?: string; question_id?: number; [key: string]: unknown }[], {
      db_id: source,
      db_name: `${source} — Query Documentation`,
    })
    return new NextResponse(md, {
      headers: {
        'Content-Type': 'text/markdown',
        'Content-Disposition': `attachment; filename="queries_${source.replace('-', '_')}.md"`,
      },
    })
  }

  if (fmt === 'doccano') {
    const lines = queries.map((q) => {
      const rec = q as Record<string, unknown>
      const text = [
        `Query ${rec.question_id ?? rec.number ?? '?'}`,
        String(rec.question ?? rec.title ?? '').slice(0, 500),
        String(rec.sql ?? '').slice(0, 200),
      ].join('\n')
      const label = rec.audit_status ? [String(rec.audit_status)] : []
      return JSON.stringify({ text, label })
    })
    const jsonl = lines.join('\n')
    return new NextResponse(jsonl, {
      headers: {
        'Content-Type': 'application/x-ndjson',
        'Content-Disposition': `attachment; filename="doccano_${source.replace('-', '_')}.jsonl"`,
      },
    })
  }

  if (fmt === 'csv') {
    const cols = [
      'question_id', 'db_id', 'question', 'SQL', 'evidence', 'difficulty',
      'query_category', 'tables_used', 'expected_output',
      'task_status', 'audit_status', 'created_at', 'updated_at',
    ]
    const escape = (s: string) => `"${String(s).replace(/"/g, '""')}"`
    const normalize = (q: Record<string, unknown>) => ({
      question_id: q.question_id ?? q.number ?? '',
      db_id: q.db_id ?? source ?? '',
      question: q.question ?? q.title ?? '',
      SQL: q.SQL ?? q.sql ?? '',
      evidence: q.evidence ?? '',
      difficulty: q.difficulty ?? '',
      query_category: q.query_category ?? '',
      tables_used: q.tables_used ?? [],
      expected_output: q.expected_output ?? '',
      task_status: q.task_status ?? '',
      audit_status: q.audit_status ?? '',
      created_at: q.created_at ?? '',
      updated_at: q.updated_at ?? '',
    })
    const rows = queries.map((q) => {
      const n = normalize(q as Record<string, unknown>)
      const tablesStr = Array.isArray(n.tables_used) ? n.tables_used.join(', ') : String(n.tables_used)
      return cols.map((c) => {
        const v = c === 'tables_used' ? tablesStr : (n as Record<string, unknown>)[c]
        return escape(String(v ?? ''))
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

  return NextResponse.json({ error: 'format must be csv, json, md, or doccano' }, { status: 400 })
}
