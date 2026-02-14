#!/usr/bin/env node
/**
 * CLI for queries.md ↔ queries.json conversion.
 * Usage:
 *   node cli.js md-to-json <queries.md> [queries.json]
 *   node cli.js json-to-md <queries.json> [queries.md]
 *   node cli.js sync <source>  # sync both files for db-N or template
 */
import { resolve, join, dirname } from 'path'
import { existsSync, readFileSync, writeFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { mdToJson, jsonToMd, convertFile } from './index.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..', '..')
const SOURCE = join(ROOT, 'source')
const TEMPLATE = join(ROOT, 'template')

function getQueriesPaths(source) {
  if (source === 'template') {
    return {
      md: join(TEMPLATE, 'queries.md'),
      json: join(TEMPLATE, 'queries.json'),
    }
  }
  const num = parseInt(String(source).replace('db-', ''), 10)
  if (isNaN(num)) return null
  const base = join(SOURCE, `db-${num}`, 'app', 'QUERIES')
  return {
    md: join(base, 'queries.md'),
    json: join(base, 'queries.json'),
  }
}

async function main() {
  const [cmd, arg1, arg2] = process.argv.slice(2)
  if (!cmd || !arg1) {
    console.error(`Usage:
  queries-convert md-to-json <queries.md> [queries.json]
  queries-convert json-to-md <queries.json> [queries.md]
  queries-convert sync <source>   # source: db-1, db-2, ..., template
`)
    process.exit(1)
  }

  if (cmd === 'sync') {
    const paths = getQueriesPaths(arg1)
    if (!paths) {
      console.error('Invalid source. Use db-1, db-2, ... or template')
      process.exit(1)
    }
    if (existsSync(paths.md) && existsSync(paths.json)) {
      console.error('Both files exist. Use md-to-json or json-to-md to pick source of truth.')
      process.exit(1)
    }
    if (existsSync(paths.md)) {
      convertFile(paths.md, paths.json, 'md-to-json')
      console.log(`Synced: ${paths.md} → ${paths.json}`)
    } else if (existsSync(paths.json)) {
      const data = JSON.parse(readFileSync(paths.json, 'utf-8'))
      const queries = Array.isArray(data) ? data : data?.queries ?? []
      const dbId = arg1 === 'template' ? 'healthcare_hospital' : arg1
      const md = jsonToMd(queries, { db_id: dbId })
      writeFileSync(paths.md, md, 'utf-8')
      console.log(`Synced: ${paths.json} → ${paths.md}`)
    } else {
      console.error('Neither queries.md nor queries.json found at', paths.md)
      process.exit(1)
    }
    return
  }

  if (cmd === 'md-to-json') {
    const out = arg2 || arg1.replace(/\.md$/i, '.json')
    convertFile(arg1, out, 'md-to-json')
    console.log(`Converted: ${arg1} → ${out}`)
    return
  }

  if (cmd === 'json-to-md') {
    const out = arg2 || arg1.replace(/\.json$/i, '.md')
    convertFile(arg1, out, 'json-to-md')
    console.log(`Converted: ${arg1} → ${out}`)
    return
  }

  console.error('Unknown command:', cmd)
  process.exit(1)
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
