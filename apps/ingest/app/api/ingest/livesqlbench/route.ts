import { NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'

/** LiveSQLBench instance shape (birdsql/livesqlbench-base-lite, livesqlbench-base-full-v1) */
export interface LiveSQLBenchInstance {
  instance_id?: string
  selected_database?: string
  query?: string
  preprocess_sql?: string[]
  clean_up_sqls?: string[]
  sol_sql?: string[]
  external_knowledges?: unknown[]
  test_cases?: unknown[]
  category?: string
  high_level?: boolean
  conditions?: Record<string, unknown>
  difficulty_tier?: string
}

function isLiveSQLBenchInstance(obj: unknown): obj is LiveSQLBenchInstance {
  if (!obj || typeof obj !== 'object') return false
  const o = obj as Record<string, unknown>
  const hasInstanceId = typeof o.instance_id === 'string'
  const hasDatabase = typeof o.selected_database === 'string'
  const hasQuery = typeof o.query === 'string'
  if (!hasInstanceId && !hasDatabase && !hasQuery) return false
  return (
    (typeof o.instance_id === 'string' || o.instance_id == null) &&
    (typeof o.selected_database === 'string' || o.selected_database == null) &&
    (typeof o.query === 'string' || o.query == null)
  )
}

export async function POST(req: Request) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  if (session.user !== 'staff') {
    return NextResponse.json({ error: 'Staff only' }, { status: 403 })
  }

  let body: unknown
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  }

  const items: LiveSQLBenchInstance[] = []
  if (Array.isArray(body)) {
    for (const item of body) {
      if (isLiveSQLBenchInstance(item)) items.push(item)
    }
  } else if (isLiveSQLBenchInstance(body)) {
    items.push(body)
  } else {
    return NextResponse.json(
      { error: 'Body must be a LiveSQLBench instance or array of instances' },
      { status: 400 }
    )
  }

  const databases = [...new Set(items.map((i) => i.selected_database).filter(Boolean))] as string[]
  const categories = [...new Set(items.map((i) => i.category).filter(Boolean))] as string[]
  const difficultyTiers = [...new Set(items.map((i) => i.difficulty_tier).filter(Boolean))] as string[]

  return NextResponse.json({
    ok: true,
    ingested: items.length,
    databases,
    categories,
    difficulty_tiers: difficultyTiers,
    sample: items[0]
      ? {
          instance_id: items[0].instance_id,
          selected_database: items[0].selected_database,
          query: items[0].query?.slice(0, 120),
          category: items[0].category,
          difficulty_tier: items[0].difficulty_tier,
        }
      : null,
  })
}
