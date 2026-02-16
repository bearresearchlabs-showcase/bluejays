import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { loadQueries } from '@/lib/data'
import {
  validateSqlSyntax,
  detectMaterializedView,
  validateMaterializedView,
} from '@/lib/sql-validator'
import { explainQuery, executeQuery, getPgConfig } from '@/lib/sql-executor'

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  if (session.user !== 'staff') {
    return NextResponse.json({ error: 'Staff only' }, { status: 403 })
  }

  const source = request.nextUrl.searchParams.get('source')
  const queryParam = request.nextUrl.searchParams.get('query')
  const role = request.nextUrl.searchParams.get('role') ?? 'staff'
  const view = request.nextUrl.searchParams.get('view') ?? '/customer'

  if (!source) {
    return NextResponse.json({ error: 'source required' }, { status: 400 })
  }

  const queryNum = queryParam ? parseInt(queryParam, 10) : 1
  const { queries, error } = loadQueries(source)
  if (error) {
    return NextResponse.json({ error }, { status: 404 })
  }

  const q =
    queries.find((x) => (x.number ?? x.question_id) === queryNum) ??
    queries[queryNum - 1]
  const sql = q ? String(q.sql ?? q.SQL ?? '') : ''
  if (!sql) {
    return NextResponse.json({ error: `Query ${queryNum} not found` }, { status: 404 })
  }

  return runValidation(sql, role, view)
}

export async function POST(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  if (session.user !== 'staff') {
    return NextResponse.json({ error: 'Staff only' }, { status: 403 })
  }

  let body: { source?: string; queryNumber?: number; role?: string; view?: string; sql?: string }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
  }

  const { source, queryNumber, role = 'staff', view = '/customer', sql: bodySql } = body

  let sql = bodySql
  if (typeof sql !== 'string' && source) {
    const { queries, error } = loadQueries(source)
    if (error) {
      return NextResponse.json({ error }, { status: 404 })
    }
    const num = queryNumber ?? 1
    const q =
      queries.find((x) => (x.number ?? x.question_id) === num) ?? queries[num - 1]
    sql = q ? String(q.sql ?? q.SQL ?? '') : ''
  }

  if (typeof sql !== 'string' || !sql.trim()) {
    return NextResponse.json({ error: 'sql or source+queryNumber required' }, { status: 400 })
  }

  return runValidation(sql, role, view)
}

async function runValidation(
  sql: string,
  role: string,
  view: string
): Promise<NextResponse> {
  const syntax = validateSqlSyntax(sql)
  const materializedView = detectMaterializedView(sql)
  const mvResult = validateMaterializedView(sql)

  const allErrors = [...syntax.errors]
  if (materializedView && mvResult.errors.length > 0) {
    allErrors.push(...mvResult.errors)
  }

  const valid = syntax.valid && (!materializedView || mvResult.valid)

  const result: {
    valid: boolean
    errors: string[]
    warnings: string[]
    materializedView: boolean
    executionResult?: { rows: Record<string, unknown>[]; columns: string[]; rowCount: number }
    executionTimeMs?: number
  } = {
    valid,
    errors: allErrors,
    warnings: syntax.warnings,
    materializedView,
  }

  const cfg = getPgConfig()
  if (cfg) {
    const start = Date.now()
    const explainRes = await explainQuery(sql, cfg)
    if (explainRes.valid) {
      const execRes = await executeQuery(sql, 10, cfg)
      if (execRes) {
        result.executionResult = execRes
      }
    } else if (explainRes.error) {
      result.errors.push(`EXPLAIN failed: ${explainRes.error}`)
    }
    result.executionTimeMs = Date.now() - start
  }

  return NextResponse.json({ ...result, role, view })
}
