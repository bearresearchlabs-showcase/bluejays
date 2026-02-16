'use client'

export interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
  materializedView: boolean
  executionResult?: {
    rows: Record<string, unknown>[]
    columns: string[]
    rowCount: number
  }
  executionTimeMs?: number
}

interface ValidationSidePanelProps {
  result: ValidationResult | null
  loading?: boolean
  queryTitle?: string
}

export function ValidationSidePanel({
  result,
  loading = false,
  queryTitle,
}: ValidationSidePanelProps) {
  const panelStyle: React.CSSProperties = {
    marginTop: '1rem',
    padding: '1rem',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    fontSize: '0.8125rem',
  }

  if (!result && !loading) {
    return (
      <aside style={panelStyle}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>
          Validation
        </h3>
        <p style={{ color: 'var(--fg-muted)' }}>Select a query to see validation details and outputs.</p>
      </aside>
    )
  }

  if (loading) {
    return (
      <aside style={panelStyle}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--fg)' }}>
          Validation
        </h3>
        <p style={{ color: 'var(--fg-muted)' }}>Validating…</p>
      </aside>
    )
  }

  if (!result) return null

  const { valid, errors, warnings, materializedView, executionResult, executionTimeMs } = result

  return (
    <aside style={panelStyle}>
      <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--fg)' }}>
        Validation {queryTitle && `— ${queryTitle}`}
      </h3>

      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        <span
          style={{
            padding: '0.2rem 0.5rem',
            borderRadius: 4,
            fontSize: '0.75rem',
            fontWeight: 600,
            background: valid ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)',
            color: valid ? 'var(--success, #22c55e)' : 'var(--error, #ef4444)',
          }}
        >
          {valid ? 'Pass' : 'Fail'}
        </span>
        {materializedView && (
          <span
            style={{
              padding: '0.2rem 0.5rem',
              borderRadius: 4,
              fontSize: '0.75rem',
              fontWeight: 600,
              background: 'rgba(59,130,246,0.2)',
              color: 'var(--accent, #3b82f6)',
            }}
          >
            Materialized View
          </span>
        )}
      </div>

      {errors.length > 0 && (
        <div style={{ marginBottom: '0.75rem' }}>
          <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--error, #ef4444)', marginBottom: '0.25rem' }}>
            Errors
          </h4>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--fg)' }}>
            {errors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div style={{ marginBottom: '0.75rem' }}>
          <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--warning, #f59e0b)', marginBottom: '0.25rem' }}>
            Warnings
          </h4>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--fg)' }}>
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {executionResult ? (
        <div style={{ marginTop: '0.75rem' }}>
          <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--fg)', marginBottom: '0.5rem' }}>
            Material View (Output)
          </h4>
          <div style={{ overflowX: 'auto', maxHeight: 200, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: 4 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem' }}>
              <thead>
                <tr>
                  {executionResult.columns.map((c) => (
                    <th
                      key={c}
                      style={{
                        padding: '0.375rem 0.5rem',
                        textAlign: 'left',
                        borderBottom: '1px solid var(--border)',
                        background: 'var(--bg)',
                        fontWeight: 600,
                      }}
                    >
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {executionResult.rows.map((row, i) => (
                  <tr key={i}>
                    {executionResult.columns.map((col) => (
                      <td
                        key={col}
                        style={{
                          padding: '0.375rem 0.5rem',
                          borderBottom: '1px solid var(--border)',
                        }}
                      >
                        {String(row[col] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ marginTop: '0.5rem', color: 'var(--fg-muted)', fontSize: '0.75rem' }}>
            {executionResult.rowCount} row(s)
            {executionTimeMs != null && ` · ${executionTimeMs}ms`}
          </p>
        </div>
      ) : (
        executionTimeMs == null && (
          <p style={{ color: 'var(--fg-muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
            Database not configured. Set PG_HOST and PG_DATABASE for execution results.
          </p>
        )
      )}

      {executionTimeMs != null && !executionResult && (
        <p style={{ color: 'var(--fg-muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
          Execution: {executionTimeMs}ms (no rows returned)
        </p>
      )}
    </aside>
  )
}
