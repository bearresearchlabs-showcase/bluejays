/**
 * Format queries.json → queries.md (template format).
 * Matches template/queries.md structure (queries_format_schema.yaml).
 */
function normalizeQuery(q, dbId) {
  const num = q.question_id ?? q.number ?? 0
  const question = q.question ?? q.title ?? q.use_case ?? `Query ${num}`
  const normalQuery = q.normal_query ?? q.normalQuery ?? ''
  const sql = q.SQL ?? q.sql ?? ''
  const evidence = q.evidence ?? q.description ?? ''
  const difficulty = ['simple', 'moderate', 'challenging'].includes(String(q.difficulty || '').toLowerCase())
    ? String(q.difficulty).toLowerCase()
    : 'moderate'
  const category = q.query_category ?? 'aggregation'
  const tables = q.tables_used ?? []
  const schemaCtx = q.schema_context ?? {}
  const expected = q.expected_output ?? '[]'

  const out = {
    db_id: dbId,
    question_id: num,
    question,
    SQL: sql,
    evidence,
    difficulty,
    query_category: category,
    tables_used: Array.isArray(tables) ? tables : [],
    schema_context: schemaCtx,
    expected_output: expected,
  }
  if (normalQuery) out.normal_query = normalQuery
  return out
}

function formatQueryBlock(q, dbId) {
  const nq = normalizeQuery(q, dbId)
  const header = `### Query ${nq.question_id} — ${nq.difficulty} / ${nq.query_category}`
  const out = {
    db_id: nq.db_id,
    question_id: nq.question_id,
    question: nq.question,
    SQL: nq.SQL,
    evidence: nq.evidence,
    difficulty: nq.difficulty,
    query_category: nq.query_category,
    tables_used: nq.tables_used,
    schema_context: nq.schema_context,
    expected_output: nq.expected_output,
  }
  if (nq.normal_query) out.normal_query = nq.normal_query
  const jsonStr = JSON.stringify(out, null, 2)
  return `${header}\n\n\`\`\`json\n${jsonStr}\n\`\`\`\n`
}

/**
 * @param {object[]} queries - Query objects
 * @param {object} opts - { db_id, db_name, overview_yaml, purpose_text, use_case_text, business_value_text, schema_sql, domain_knowledge_text, difficulty_dist_text }
 * @returns {string} queries.md content
 */
export function formatQueriesMd(queries, opts = {}) {
  const dbId = opts.db_id ?? 'db-1'
  const dbName = opts.db_name ?? `Database ${dbId}`
  const overviewYaml = opts.overview_yaml ?? `db_id: ${dbId}
domain: Database domain
source: [synthetic / open / commercial]
license_type: [Commercial / Open / Academic]
license_cost: [Annual cost if applicable]
tables: 0
total_rows: ~0
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
`
  const purposeText = opts.purpose_text ?? `This database supports analytics for ${dbId}.`
  const useCaseText = opts.use_case_text ?? `Target use cases for ${dbId}: analytics, reporting, dashboards.`
  const businessValueText = opts.business_value_text ?? `Business value for ${dbId}.`
  const schemaSql = opts.schema_sql ?? '-- Schema from schema.sql'
  const domainKnowledge = opts.domain_knowledge_text ?? 'Domain-specific concepts for this database.'
  const difficultyDist = opts.difficulty_dist_text ?? `Target distribution across 30 queries:
- simple (10): Single-table, basic aggregation
- moderate (12): 2-3 table joins, GROUP BY
- challenging (8): CTEs, window functions
`

  const parts = [
    `# ${dbName} — Query Documentation\n`,
    '## Database Overview\n',
    '```yaml',
    overviewYaml.trim(),
    '```\n',
    '## Purpose\n',
    '```text',
    purposeText.trim(),
    '```\n',
    '## Use Case\n',
    '```text',
    useCaseText.trim(),
    '```\n',
    '## Business Value\n',
    '```text',
    businessValueText.trim(),
    '```\n',
    '## Schema\n',
    '```sql',
    schemaSql.trim(),
    '```\n',
    '## Domain Knowledge\n',
    '```text',
    domainKnowledge.trim(),
    '```\n',
    '## Query Difficulty Distribution\n',
    '```text',
    difficultyDist.trim(),
    '```\n',
    '## Queries\n',
  ]

  const validQueries = queries.filter((q) => q && typeof q === 'object' && ('question_id' in q || 'question' in q || 'SQL' in q || 'sql' in q))
  for (const q of validQueries) {
    parts.push(formatQueryBlock(q, dbId))
  }

  return parts.join('\n')
}
