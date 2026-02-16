'use client'

import { useEffect, useRef } from 'react'
import Prism from 'prismjs'
import 'prismjs/components/prism-sql'

export function SqlCodeBlock({ sql, maxHeight = 400 }: { sql: string; maxHeight?: number }) {
  const ref = useRef<HTMLPreElement>(null)

  useEffect(() => {
    if (!ref.current || !sql) return
    Prism.highlightElement(ref.current)
  }, [sql])

  return (
    <pre
      ref={ref}
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '1rem 1.25rem',
        overflow: 'auto',
        maxHeight,
        fontSize: '0.8125rem',
        fontFamily: 'ui-monospace, monospace',
        lineHeight: 1.5,
        margin: 0,
      }}
    >
      <code className="language-sql">{sql}</code>
    </pre>
  )
}
