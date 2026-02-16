/**
 * Optional SQL execution against PostgreSQL.
 * Uses pg client when PG_* env vars are set; otherwise skips.
 */

export interface PgConfig {
  host: string
  port: number
  user: string
  password: string
  database: string
}

export interface ExplainResult {
  valid: boolean
  plan?: string
  error?: string
}

export interface ExecutionResult {
  rows: Record<string, unknown>[]
  columns: string[]
  rowCount: number
}

/**
 * Get PostgreSQL config from environment. Returns null when not configured.
 */
export function getPgConfig(): PgConfig | null {
  const host = process.env.PG_HOST
  const database = process.env.PG_DATABASE
  if (!host || !database) return null

  return {
    host,
    port: parseInt(process.env.PG_PORT ?? '5432', 10),
    user: process.env.PG_USER ?? 'postgres',
    password: process.env.PG_PASSWORD ?? '',
    database,
  }
}

/**
 * Add LIMIT to SELECT query for safe execution. Does not modify non-SELECT.
 */
function addLimit(sql: string, limit: number): string {
  const trimmed = sql.trim().replace(/;\s*$/, '')
  const upper = trimmed.toUpperCase()
  if (!upper.startsWith('SELECT') && !upper.startsWith('WITH')) {
    return sql
  }
  if (upper.includes('LIMIT ')) {
    return sql
  }
  return `${trimmed} LIMIT ${limit}`
}

/**
 * Run EXPLAIN on query to validate syntax. Returns valid when EXPLAIN succeeds.
 */
export async function explainQuery(
  sql: string,
  config?: PgConfig | null
): Promise<ExplainResult> {
  const cfg = config ?? getPgConfig()
  if (!cfg) {
    return { valid: false, error: 'PostgreSQL not configured' }
  }

  try {
    const { Client } = await import('pg')
    const client = new Client({
      host: cfg.host,
      port: cfg.port,
      user: cfg.user,
      password: cfg.password,
      database: cfg.database,
    })
    await client.connect()
    try {
      const res = await client.query(`EXPLAIN ${sql}`)
      const plan = res.rows.map((r) => JSON.stringify(r)).join('\n')
      return { valid: true, plan }
    } finally {
      await client.end()
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err)
    return { valid: false, error: msg }
  }
}

/**
 * Execute query with LIMIT and return rows. For SELECT/WITH only.
 */
export async function executeQuery(
  sql: string,
  limit: number,
  config?: PgConfig | null
): Promise<{ rows: Record<string, unknown>[]; columns: string[]; rowCount: number } | null> {
  const cfg = config ?? getPgConfig()
  if (!cfg) return null

  try {
    const { Client } = await import('pg')
    const client = new Client({
      host: cfg.host,
      port: cfg.port,
      user: cfg.user,
      password: cfg.password,
      database: cfg.database,
    })
    await client.connect()
    try {
      const limited = addLimit(sql, limit)
      const res = await client.query(limited)
      const columns = res.fields?.map((f) => f.name) ?? []
      const rows = (res.rows ?? []) as Record<string, unknown>[]
      return { rows, columns, rowCount: rows.length }
    } finally {
      await client.end()
    }
  } catch {
    return null
  }
}
