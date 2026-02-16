/**
 * Build intent-focused display text for queries (LiveSQLBench / BenchPress style).
 * Prefer: natural_language_query > intent > combined use_case + business_value + purpose + description.
 */

export interface QueryForIntent {
  natural_language_query?: string
  intent?: string
  use_case?: string
  business_value?: string
  purpose?: string
  description?: string
}

/**
 * Build intent-focused display text from query metadata.
 * Used for website display and Qdrant embedding text.
 */
export function buildIntentDisplay(q: QueryForIntent): string {
  if (q.natural_language_query?.trim()) return q.natural_language_query.trim()
  if (q.intent?.trim()) return q.intent.trim()
  const parts: string[] = []
  if (q.use_case?.trim()) parts.push(q.use_case.trim())
  if (q.business_value?.trim()) parts.push(q.business_value.trim())
  if (q.purpose?.trim()) parts.push(q.purpose.trim())
  if (q.description?.trim()) {
    const d = q.description.trim()
    if (!parts.some(p => d.includes(p))) parts.push(d)
  }
  return parts.join(' ') || (q.description || '').trim()
}
