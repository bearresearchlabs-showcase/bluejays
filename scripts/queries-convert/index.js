/**
 * queries-convert — Bidirectional queries.md ↔ queries.json
 * Uses MDX ecosystem (remark) for parsing; template format per queries_format_schema.yaml.
 * Works locally and via API.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import { parseQueriesMd } from './parse-md.js'
import { formatQueriesMd } from './format-md.js'

const __dirname = dirname(fileURLToPath(import.meta.url))

/**
 * Parse queries.md → { queries, title, sections }
 */
export function mdToJson(mdContent) {
  const { queries, title, sections } = parseQueriesMd(mdContent)
  return {
    meta: { title, sections },
    queries,
    source_file: 'queries.md',
  }
}

/**
 * Format queries (array or { queries }) → queries.md string
 */
export function jsonToMd(queriesOrData, opts = {}) {
  const queries = Array.isArray(queriesOrData)
    ? queriesOrData
    : queriesOrData?.queries ?? queriesOrData?.data?.queries ?? []
  return formatQueriesMd(queries, opts)
}

/**
 * Load from file, convert md→json or json→md
 * @param {string} inputPath
 * @param {string} [outputPath]
 * @param {'md-to-json'|'json-to-md'} direction
 * @param {object} [opts] - For json-to-md: db_id, db_name, etc.
 */
export function convertFile(inputPath, outputPath, direction, opts = {}) {
  if (!existsSync(inputPath)) {
    throw new Error(`File not found: ${inputPath}`)
  }
  const content = readFileSync(inputPath, 'utf-8')
  let result
  if (direction === 'md-to-json') {
    const data = mdToJson(content)
    result = JSON.stringify(data.queries?.length ? data.queries : data, null, 2)
  } else {
    const data = JSON.parse(content)
    let queries = Array.isArray(data) ? data : data?.queries ?? data?.data?.queries ?? []
    queries = queries.filter((q) => q && typeof q === 'object' && ('question_id' in q || 'question' in q || 'SQL' in q || 'sql' in q))
    const dbId = data?.meta?.db_id ?? opts?.db_id ?? 'db-1'
    result = jsonToMd(queries, { db_id: dbId, ...opts })
  }
  if (outputPath) {
    const outDir = dirname(outputPath)
    if (outDir && !existsSync(outDir)) {
      mkdirSync(outDir, { recursive: true })
    }
    writeFileSync(outputPath, result, 'utf-8')
  }
  return result
}

export { parseQueriesMd, formatQueriesMd }
