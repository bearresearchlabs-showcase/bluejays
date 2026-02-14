/**
 * Parse queries.md to structured data (sections + queries).
 * Matches template/queries_format_schema.yaml structure.
 * Query block: ### Query N — difficulty / category + ```json block
 */
const QUERY_HEADER_RE = /^### Query (\d+) — (simple|moderate|challenging) \/ ([a-zA-Z0-9/_-]+)\s*$/m
const QUERIES_SECTION_RE = /^## Queries\s*$/m

/**
 * @param {string} md - queries.md content
 * @returns {{ sections: Record<string, string>, queries: object[], title?: string }}
 */
export function parseQueriesMd(md) {
  const sections = {}
  const queries = []
  let title = null

  // Extract title
  const titleMatch = md.match(/^# (.+) — Query Documentation\s*$/m)
  if (titleMatch) title = titleMatch[1]

  // Find ## Queries section
  const queriesIdx = md.search(QUERIES_SECTION_RE)
  if (queriesIdx < 0) return { sections, queries, title }

  const queriesSection = md.slice(queriesIdx)
  const blocks = queriesSection.split(/(?=### Query \d+ — )/m)

  for (let i = 1; i < blocks.length; i++) {
    const block = blocks[i]
    const headerMatch = block.match(/^### Query (\d+) — (simple|moderate|challenging) \/ ([a-zA-Z0-9/_-]+)\s*\n+/)
    if (!headerMatch) continue

    const jsonMatch = block.match(/```json\s*\n([\s\S]*?)\n```/)
    if (!jsonMatch) continue

    try {
      const q = JSON.parse(jsonMatch[1].trim())
      queries.push(q)
    } catch (_) {
      // skip malformed JSON
    }
  }

  return { sections, queries, title }
}
