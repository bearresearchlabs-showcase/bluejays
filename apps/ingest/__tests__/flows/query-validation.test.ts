/**
 * Flow: Query validation
 * Assert queries.json structure per db: 30 queries, required fields (number, title, sql, etc.).
 */
import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

const EXPECTED_QUERY_COUNT = 30

function loadQueriesJson(dbPath: string): { queries: unknown[]; total_queries?: number } | null {
  const candidates = [
    join(dbPath, 'app', 'QUERIES', 'queries.json'),
    join(dbPath, 'queries', 'queries.json'),
    join(dbPath, 'queries.json'), // template has queries.json at root
  ]
  for (const p of candidates) {
    if (existsSync(p)) {
      const raw = readFileSync(p, 'utf-8')
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) return { queries: parsed, total_queries: parsed.length }
      return parsed as { queries: unknown[]; total_queries?: number }
    }
  }
  return null
}

function validateQuery(q: unknown): string[] {
  const errs: string[] = []
  const obj = q as Record<string, unknown>
  const titleVal = obj.title ?? obj.question
  if (titleVal == null || titleVal === '') {
    errs.push('Missing or empty field: title')
  }
  const numVal = obj.number ?? obj.question_id
  if (numVal == null || numVal === '') {
    errs.push('Missing or empty field: number')
  }
  const sqlVal = obj.sql ?? obj.SQL
  if (typeof sqlVal !== 'string' || sqlVal.trim().length === 0) {
    errs.push('sql must be non-empty string')
  }
  if (numVal != null && typeof numVal !== 'number' && typeof numVal !== 'string') {
    errs.push('number must be number or string')
  }
  return errs
}

// Repo root (apps/ingest/__tests__/flows -> ../../.. = repo root)
const REPO_ROOT = join(__dirname, '..', '..', '..', '..')

describe('Query validation flow', () => {
  it('source/db-1 has valid queries.json with 30 queries', () => {
    const root = REPO_ROOT
    const dbPath = join(root, 'source', 'db-1')
    const data = loadQueriesJson(dbPath)
    expect(data).not.toBeNull()
    expect(data!.queries).toBeDefined()
    expect(Array.isArray(data!.queries)).toBe(true)
    expect(data!.queries.length).toBe(EXPECTED_QUERY_COUNT)
    expect(data!.total_queries).toBe(EXPECTED_QUERY_COUNT)
  })

  it('each query has required fields: number, title, sql', () => {
    const root = REPO_ROOT
    const dbPath = join(root, 'source', 'db-1')
    const data = loadQueriesJson(dbPath)
    expect(data).not.toBeNull()
    const queries = data!.queries

    for (let i = 0; i < queries.length; i++) {
      const errs = validateQuery(queries[i])
      expect(errs).toEqual([])
    }
  })

  it('queries are numbered sequentially 1..30', () => {
    const root = REPO_ROOT
    const dbPath = join(root, 'source', 'db-1')
    const data = loadQueriesJson(dbPath)
    expect(data).not.toBeNull()
    const queries = data!.queries as Array<{ number: number }>

    for (let i = 0; i < queries.length; i++) {
      expect(queries[i].number).toBe(i + 1)
    }
  })

  it('template has valid queries.json when present', () => {
    const root = REPO_ROOT
    const templatePath = join(root, 'template')
    const data = loadQueriesJson(templatePath)
    if (!data) {
      const appPath = join(root, 'source', 'db-1')
      const fallback = loadQueriesJson(appPath)
      expect(fallback).not.toBeNull()
      return
    }
    expect(data.queries).toBeDefined()
    expect(Array.isArray(data.queries)).toBe(true)
    expect(data.queries.length).toBeGreaterThan(0)
  })
})
