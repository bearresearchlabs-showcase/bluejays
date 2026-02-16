import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { loadQueries } from '@/lib/data'
import {
  validateSqlSyntax,
  detectMaterializedView,
  validateMaterializedView,
} from '@/lib/sql-validator'
import { getPgConfig } from '@/lib/sql-executor'

export async function POST(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  if (session.user !== 'staff') {
    return NextResponse.json({ error: 'Staff only' }, { status: 403 })
  }

  let body: { source?: string; role?: string; view?: string }
  try {
    body = (await request.json()) ?? {}
  } catch {
    body = {}
  }

  const { source, role = 'staff', view = '/customer' } = body

  if (!source) {
    return NextResponse.json({ error: 'source required' }, { status: 400 })
  }

  const { queries, error } = loadQueries(source)
  if (error) {
    return NextResponse.json({ error }, { status: 404 })
  }

  const hasPg = !!getPgConfig()

  const results = queries.map((q, idx) => {
    const sql = String(q.sql ?? q.SQL ?? '')
    const num = (q.number ?? q.question_id ?? idx + 1) as number
    const title = String(q.title ?? q.question ?? `Query ${num}`)

    const syntax = validateSqlSyntax(sql)
    const materializedView = detectMaterializedView(sql)
    const mvResult = validateMaterializedView(sql)

    const allErrors = [...syntax.errors]
    if (materializedView && mvResult.errors.length > 0) {
      allErrors.push(...mvResult.errors)
    }

    const valid = syntax.valid && (!materializedView || mvResult.valid)

    return {
      queryNumber: num,
      title: title.slice(0, 80),
      valid,
      errors: allErrors,
      warnings: syntax.warnings,
      materializedView,
      hasExecutionResult: hasPg && valid,
    }
  })

  return NextResponse.json({ results, role, view })
}
