/**
 * Converts PostgreSQL schema.sql to DBML for dbdiagram.io, ChartDB, etc.
 * Parses CREATE TABLE statements and outputs DBML format.
 */

export interface ParsedColumn {
  name: string
  type: string
  pk: boolean
  ref?: { table: string; column: string }
  notNull: boolean
  unique: boolean
}

export interface ParsedTable {
  name: string
  columns: ParsedColumn[]
  compositePk?: string[]
}

function pgTypeToDbml(pgType: string): string {
  const t = pgType.toUpperCase()
  if (t.includes('UUID')) return 'uuid'
  if (t.includes('VARCHAR') || t.includes('CHARACTER')) return 'varchar'
  if (t === 'TEXT') return 'text'
  if (t.includes('BOOLEAN') || t === 'BOOL') return 'boolean'
  if (t.includes('SERIAL') || t.includes('INT') || t.includes('BIGINT') || t.includes('SMALLINT')) return 'int'
  if (t.includes('NUMERIC') || t.includes('DECIMAL') || t.includes('REAL') || t.includes('DOUBLE')) return 'decimal'
  if (t.includes('TIMESTAMP') || t.includes('DATE') || t.includes('TIME')) return 'timestamp'
  return 'varchar'
}

function extractTableBody(sql: string, start: number): { body: string; end: number } | null {
  const open = sql.indexOf('(', start)
  if (open === -1) return null
  let depth = 1
  let i = open + 1
  while (i < sql.length && depth > 0) {
    const c = sql[i]
    if (c === '(') depth++
    else if (c === ')') depth--
    i++
  }
  return { body: sql.slice(open + 1, i - 1), end: i }
}

function parseCreateTable(sql: string): ParsedTable[] {
  const tables: ParsedTable[] = []
  const createTableRe = /CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["']?(\w+)["']?\s*/gi
  let m: RegExpExecArray | null
  while ((m = createTableRe.exec(sql)) !== null) {
    const tableName = m[1]
    const extracted = extractTableBody(sql, m.index + m[0].length)
    if (!extracted) continue
    const body = extracted.body
    const columns: ParsedColumn[] = []
    let compositePk: string[] | undefined

    // Parse PRIMARY KEY (col1, col2)
    const pkMatch = body.match(/PRIMARY\s+KEY\s*\(\s*([^)]+)\s*\)/i)
    if (pkMatch) {
      compositePk = pkMatch[1].split(',').map((c) => c.trim().replace(/^["']?|["']?$/g, ''))
    }

    // Parse each line (column definition)
    const lines = body.split('\n').map((l) => l.trim()).filter(Boolean)
    for (const line of lines) {
      if (/^PRIMARY\s+KEY\s*\(/i.test(line) || /^FOREIGN\s+KEY/i.test(line) || /^CONSTRAINT\s+/i.test(line) || /^UNIQUE\s*\(/i.test(line)) {
        continue
      }
      const colMatch = line.match(/^["']?(\w+)["']?\s+(\S+(?:\s*\([^)]+\))?)\s*(.*)$/i)
      if (!colMatch) continue

      const colName = colMatch[1]
      const pgType = colMatch[2]
      const rest = (colMatch[3] || '').toUpperCase()

      const refMatch = line.match(/REFERENCES\s+["']?(\w+)["']?\s*\(\s*["']?(\w+)["']?\s*\)/i)
      const isPk = rest.includes('PRIMARY KEY') || (compositePk && compositePk.includes(colName))

      columns.push({
        name: colName,
        type: pgTypeToDbml(pgType),
        pk: !!isPk,
        ref: refMatch ? { table: refMatch[1], column: refMatch[2] } : undefined,
        notNull: rest.includes('NOT NULL'),
        unique: rest.includes('UNIQUE'),
      })
    }

    tables.push({ name: tableName, columns, compositePk })
  }
  return tables
}

export function schemaToDbml(schemaSql: string): string {
  const tables = parseCreateTable(schemaSql)
  const lines: string[] = []

  const refs: string[] = []
  for (const t of tables) {
    lines.push(`Table ${t.name} {`)
    for (const c of t.columns) {
      const mods: string[] = []
      if (c.pk) mods.push('pk')
      if (c.notNull) mods.push('not null')
      if (c.unique) mods.push('unique')
      const modStr = mods.length ? ` [${mods.join(', ')}]` : ''
      lines.push(`  ${c.name} ${c.type}${modStr}`)
      if (c.ref) refs.push(`Ref: ${t.name}.${c.name} > ${c.ref.table}.${c.ref.column}`)
    }
    lines.push('}')
    lines.push('')
  }
  lines.push(...refs)
  return lines.join('\n').trim()
}
