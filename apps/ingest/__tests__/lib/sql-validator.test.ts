/**
 * Unit tests for SQL validator (syntax, CTE, materialized view detection)
 */
import {
  validateSqlSyntax,
  detectMaterializedView,
  validateMaterializedView,
} from '@/lib/sql-validator'

describe('validateSqlSyntax', () => {
  it('rejects empty SQL', () => {
    const r = validateSqlSyntax('')
    expect(r.valid).toBe(false)
    expect(r.errors).toContain('Empty SQL statement')
  })

  it('rejects SQL with unbalanced parentheses', () => {
    const r = validateSqlSyntax('SELECT * FROM t WHERE (a = 1')
    expect(r.valid).toBe(false)
    expect(r.errors.some((e) => e.includes('Unbalanced parentheses'))).toBe(true)
  })

  it('rejects SQL with no keywords', () => {
    const r = validateSqlSyntax('foo bar baz')
    expect(r.valid).toBe(false)
    expect(r.errors).toContain('No SQL keywords found')
  })

  it('rejects WITH without SELECT', () => {
    const r = validateSqlSyntax('WITH cte AS (VALUES (1)) UPDATE t SET x = 1')
    expect(r.valid).toBe(false)
    expect(r.errors).toContain('WITH clause without SELECT statement')
  })

  it('rejects recursive CTE without UNION', () => {
    const r = validateSqlSyntax('WITH RECURSIVE cte AS (SELECT 1) SELECT * FROM cte')
    expect(r.valid).toBe(false)
    expect(r.errors).toContain('Recursive CTE missing UNION/UNION ALL')
  })

  it('rejects SQL Server TOP syntax', () => {
    const r = validateSqlSyntax('SELECT TOP 10 * FROM t')
    expect(r.valid).toBe(false)
    expect(r.errors.some((e) => e.includes('SQL Server TOP syntax'))).toBe(true)
  })

  it('accepts valid SELECT', () => {
    const r = validateSqlSyntax('SELECT * FROM t;')
    expect(r.valid).toBe(true)
    expect(r.errors).toHaveLength(0)
  })

  it('accepts valid CTE', () => {
    const r = validateSqlSyntax('WITH cte AS (SELECT 1 AS x) SELECT * FROM cte;')
    expect(r.valid).toBe(true)
  })

  it('accepts valid recursive CTE', () => {
    const r = validateSqlSyntax(
      'WITH RECURSIVE cte AS (SELECT 1 n UNION ALL SELECT n+1 FROM cte WHERE n < 5) SELECT * FROM cte;'
    )
    expect(r.valid).toBe(true)
  })

  it('warns when SQL does not end with semicolon', () => {
    const r = validateSqlSyntax('SELECT * FROM t')
    expect(r.valid).toBe(true)
    expect(r.warnings.some((w) => w.includes('semicolon'))).toBe(true)
  })

  it('warns for PostGIS functions', () => {
    const r = validateSqlSyntax('SELECT ST_WITHIN(a, b) FROM t;')
    expect(r.valid).toBe(true)
    expect(r.warnings.some((w) => w.includes('PostGIS'))).toBe(true)
  })
})

describe('detectMaterializedView', () => {
  it('detects CREATE MATERIALIZED VIEW', () => {
    expect(
      detectMaterializedView('CREATE MATERIALIZED VIEW mv AS SELECT 1;')
    ).toBe(true)
  })

  it('detects CREATE MATERIALIZED VIEW with whitespace', () => {
    expect(
      detectMaterializedView('CREATE  MATERIALIZED  VIEW mv AS SELECT 1;')
    ).toBe(true)
  })

  it('returns false for plain CREATE VIEW', () => {
    expect(detectMaterializedView('CREATE VIEW v AS SELECT 1;')).toBe(false)
  })

  it('returns false for plain SELECT', () => {
    expect(detectMaterializedView('SELECT * FROM t;')).toBe(false)
  })
})

describe('validateMaterializedView', () => {
  it('returns valid for non-MV SQL', () => {
    const r = validateMaterializedView('SELECT * FROM t;')
    expect(r.valid).toBe(true)
    expect(r.errors).toHaveLength(0)
  })

  it('validates correct materialized view', () => {
    const r = validateMaterializedView(
      'CREATE MATERIALIZED VIEW mv AS SELECT id, name FROM users;'
    )
    expect(r.valid).toBe(true)
  })

  it('validates MV with subquery', () => {
    const r = validateMaterializedView(
      'CREATE MATERIALIZED VIEW mv AS (SELECT * FROM t);'
    )
    expect(r.valid).toBe(true)
  })

  it('reports error for malformed MV without AS SELECT', () => {
    const r = validateMaterializedView(
      'CREATE MATERIALIZED VIEW mv AS INSERT INTO t VALUES (1);'
    )
    expect(r.valid).toBe(false)
    expect(r.errors.some((e) => e.includes('AS SELECT'))).toBe(true)
  })
})
