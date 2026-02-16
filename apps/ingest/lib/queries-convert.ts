/**
 * queries.md ↔ queries.json conversion (TypeScript bridge).
 * Mirrors scripts/queries-convert for use in Next.js API routes.
 * Format per template/queries_format_schema.yaml.
 */

const QUERIES_SECTION_RE = /^## Queries\s*$/m

export interface QueryRecord {
  db_id?: string
  question_id?: number
  question?: string
  SQL?: string
  evidence?: string
  difficulty?: string
  query_category?: string
  tables_used?: string[]
  schema_context?: Record<string, unknown>
  expected_output?: string
  [key: string]: unknown
}

export function parseQueriesMd(md: string): { queries: QueryRecord[]; title?: string } {
  const queries: QueryRecord[] = []
  let title: string | null = null

  const titleMatch = md.match(/^# (.+) — Query Documentation\s*$/m)
  if (titleMatch) title = titleMatch[1]

  const queriesIdx = md.search(QUERIES_SECTION_RE)
  if (queriesIdx < 0) return { queries, title: title ?? undefined }

  const queriesSection = md.slice(queriesIdx)
  const blocks = queriesSection.split(/(?=### Query \d+ — )/m)

  for (let i = 1; i < blocks.length; i++) {
    const block = blocks[i]
    const jsonMatch = block.match(/```json\s*\n([\s\S]*?)\n```/)
    if (!jsonMatch) continue
    try {
      const q = JSON.parse(jsonMatch[1].trim()) as QueryRecord
      queries.push(q)
    } catch {
      // skip malformed
    }
  }

  return { queries, title: title ?? undefined }
}

export function formatQueriesMd(
  queries: QueryRecord[],
  opts: { db_id?: string; db_name?: string } = {}
): string {
  const dbId = opts.db_id ?? 'db-1'
  const dbName = opts.db_name ?? `Database ${dbId}`

  const normalize = (q: QueryRecord) => ({
    db_id: dbId,
    question_id: q.question_id ?? q.number ?? 0,
    question: q.question ?? q.title ?? '',
    SQL: q.SQL ?? q.sql ?? '',
    evidence: q.evidence ?? q.description ?? '',
    difficulty: ['simple', 'moderate', 'challenging'].includes(String(q.difficulty || '').toLowerCase())
      ? String(q.difficulty).toLowerCase()
      : 'moderate',
    query_category: q.query_category ?? 'aggregation',
    tables_used: Array.isArray(q.tables_used) ? q.tables_used : [],
    schema_context: q.schema_context ?? {},
    expected_output: q.expected_output ?? '[]',
  })

  const formatBlock = (q: QueryRecord) => {
    const n = normalize(q)
    const header = `### Query ${n.question_id} — ${n.difficulty} / ${n.query_category}`
    const out = {
      db_id: n.db_id,
      question_id: n.question_id,
      question: n.question,
      SQL: n.SQL,
      evidence: n.evidence,
      difficulty: n.difficulty,
      query_category: n.query_category,
      tables_used: n.tables_used,
      schema_context: n.schema_context,
      expected_output: n.expected_output,
    }
    return `${header}\n\n\`\`\`json\n${JSON.stringify(out, null, 2)}\n\`\`\`\n`
  }

  const preamble = `# ${dbName} — Query Documentation

## Database Overview

\`\`\`yaml
db_id: ${dbId}
domain: Database domain
sql_dialect: PostgreSQL
\`\`\`

## Purpose

\`\`\`text
This database supports analytics for ${dbId}.
\`\`\`

## Use Case

\`\`\`text
Target use cases: analytics, reporting, dashboards.
\`\`\`

## Business Value

\`\`\`text
Business value for ${dbId}.
\`\`\`

## Schema

\`\`\`sql
-- Schema from schema.sql
\`\`\`

## Domain Knowledge

\`\`\`text
Domain-specific concepts.
\`\`\`

## Query Difficulty Distribution

\`\`\`text
Target: simple (10), moderate (12), challenging (8).
\`\`\`

## Queries

`

  return preamble + queries.map(formatBlock).join('')
}
