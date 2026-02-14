'use client'

import { useEffect } from 'react'

// #region agent log
export function DebugPing() {
  useEffect(() => {
    fetch('http://127.0.0.1:7242/ingest/ede760b6-b9c4-4904-b4d5-a8169c1a50e4', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'DebugPing.tsx:mount',
        message: 'Annotator app mounted',
        data: { cwd: typeof window !== 'undefined' ? window.location?.href : 'ssr', hypothesisId: 'H1' },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
  }, [])
  return null
}
// #endregion
