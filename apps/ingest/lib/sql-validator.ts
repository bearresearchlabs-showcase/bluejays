/**
 * SQL validation for PostgreSQL compatibility.
 * Ported from scripts/validate_sql_syntax_postgresql.py
 */

export interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export interface MaterializedViewResult {
  valid: boolean
  errors: string[]
}

const SQL_KEYWORDS = ['SELECT', 'WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE', 'ALTER']
const POSTGIS_FUNCTIONS = ['ST_WITHIN', 'ST_DISTANCE', 'ST_INTERSECTS', 'ST_AREA']
const WINDOW_FUNCTIONS = ['ROW_NUMBER', 'RANK', 'DENSE_RANK', 'LEAD', 'LAG', 'PERCENTILE_CONT']

/**
 * Validate SQL syntax for PostgreSQL compatibility.
 */
export function validateSqlSyntax(sql: string): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  const sqlUpper = sql.toUpperCase().trim()

  if (!sqlUpper) {
    errors.push('Empty SQL statement')
    return { valid: false, errors, warnings }
  }

  // Balanced parentheses
  const openParens = (sql.match(/\(/g) ?? []).length
  const closeParens = (sql.match(/\)/g) ?? []).length
  if (openParens !== closeParens) {
    errors.push(`Unbalanced parentheses: ${openParens} open, ${closeParens} close`)
  }

  // Basic quote balance (simplified)
  const singleQuotes = (sql.match(/'/g) ?? []).length - (sql.match(/\\'/g) ?? []).length
  if (singleQuotes % 2 !== 0) {
    warnings.push('Possible unbalanced single quotes (may be escaped)')
  }

  // SQL keywords
  if (!SQL_KEYWORDS.some((kw) => sqlUpper.includes(kw))) {
    errors.push('No SQL keywords found')
  }

  // WITH without SELECT
  if (sqlUpper.includes('WITH') && !sqlUpper.includes('SELECT')) {
    errors.push('WITH clause without SELECT statement')
  }

  // SQL Server TOP syntax
  if (sqlUpper.includes('TOP ') && !sqlUpper.includes('LIMIT')) {
    errors.push('SQL Server TOP syntax (PostgreSQL uses LIMIT)')
  }

  // CTE structure
  if (sqlUpper.includes('WITH')) {
    const withCount = (sqlUpper.match(/WITH/g) ?? []).length
    const selectCount = (sqlUpper.match(/SELECT/g) ?? []).length
    if (withCount > selectCount) {
      warnings.push('More WITH clauses than SELECT statements')
    }
  }

  // Recursive CTE
  if (sqlUpper.includes('WITH RECURSIVE')) {
    if (!sqlUpper.includes('UNION') && !sqlUpper.includes('UNION ALL')) {
      errors.push('Recursive CTE missing UNION/UNION ALL')
    }
  }

  // Semicolon
  if (!sql.trim().endsWith(';')) {
    warnings.push("SQL statement doesn't end with semicolon")
  }

  // PostgreSQL-specific
  if (POSTGIS_FUNCTIONS.some((f) => sqlUpper.includes(f))) {
    warnings.push('Uses PostGIS functions - requires PostGIS extension in PostgreSQL')
  }

  if (WINDOW_FUNCTIONS.some((f) => sqlUpper.includes(f)) && !sqlUpper.includes('OVER')) {
    warnings.push('Window functions used but OVER clause not found')
  }

  if (sqlUpper.includes('PERCENTILE_CONT') && !sqlUpper.includes('WITHIN GROUP')) {
    warnings.push('PERCENTILE_CONT should use WITHIN GROUP clause')
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  }
}

/**
 * Detect if SQL creates a materialized view.
 */
export function detectMaterializedView(sql: string): boolean {
  const sqlUpper = sql.toUpperCase().trim()
  return /CREATE\s+MATERIALIZED\s+VIEW/i.test(sql) || sqlUpper.includes('CREATE MATERIALIZED VIEW')
}

/**
 * Validate materialized view SQL structure.
 */
export function validateMaterializedView(sql: string): MaterializedViewResult {
  const errors: string[] = []

  if (!detectMaterializedView(sql)) {
    return { valid: true, errors: [] }
  }

  const sqlUpper = sql.toUpperCase()

  // Must have AS SELECT or AS ( subquery )
  if (!/AS\s+\(?\s*SELECT/i.test(sql) && !/AS\s+SELECT/i.test(sqlUpper)) {
    errors.push('Materialized view must have AS SELECT or AS (SELECT ...)')
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}
