#!/usr/bin/env node
/**
 * Generate sources manifest for Vercel deploy.
 * Embeds sources + queries so app works when filesystem is unavailable (serverless).
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.join(__dirname, '..')
const SOURCE = path.join(ROOT, 'source')
const TEMPLATE = path.join(ROOT, 'template')
const outArg = process.argv.find((a) => a.startsWith('--out='))
const OUT = outArg ? path.resolve(ROOT, outArg.slice(6)) : path.join(ROOT, 'lib', 'sources-manifest.json')

function loadQueriesForSource(name) {
  if (name === 'template') {
    const p = path.join(TEMPLATE, 'queries.json')
    if (!fs.existsSync(p)) return null
    const raw = fs.readFileSync(p, 'utf-8')
    const data = JSON.parse(raw)
    return Array.isArray(data) ? data : data?.queries ?? data?.data?.queries ?? []
  }
  const num = parseInt(name.replace('db-', ''), 10)
  if (isNaN(num)) return null
  const bases = [
    path.join(SOURCE, `db-${num}`, 'app', 'QUERIES', 'queries.json'),
    path.join(SOURCE, `db-${num}`, 'QUERIES', 'queries.json'),
    path.join(ROOT, `db-${num}`, 'queries', 'queries.json'),
  ]
  for (const p of bases) {
    if (fs.existsSync(p)) {
      const raw = fs.readFileSync(p, 'utf-8')
      const data = JSON.parse(raw)
      const q = Array.isArray(data) ? data : data?.queries ?? data?.data?.queries ?? []
      return q.filter((x) => x && typeof x === 'object' && ('question_id' in x || 'question' in x || 'sql' in x || 'number' in x || 'title' in x))
    }
  }
  return null
}

const sources = ['template']
const queriesBySource = {}

const tq = loadQueriesForSource('template')
if (tq && tq.length > 0) {
  queriesBySource.template = tq
}

if (fs.existsSync(SOURCE)) {
  const dirs = fs.readdirSync(SOURCE, { withFileTypes: true })
    .filter((d) => d.isDirectory() && d.name.startsWith('db-'))
    .map((d) => d.name)
    .sort((a, b) => {
      const na = parseInt(a.replace('db-', ''), 10) || 999
      const nb = parseInt(b.replace('db-', ''), 10) || 999
      return na - nb
    })
  for (const name of dirs) {
    const q = loadQueriesForSource(name)
    if (q && q.length > 0) {
      sources.push(name)
      queriesBySource[name] = q
    }
  }
}

const manifest = { sources, queries: queriesBySource }
const manifestStr = JSON.stringify(manifest)
// On Vercel, source/ may be absent; keep committed manifest if we'd produce a worse one
const existing = (() => { try { return fs.readFileSync(OUT, 'utf-8') } catch { return null } })()
if (sources.length <= 1 && existing) {
  const existingData = JSON.parse(existing)
  if (Array.isArray(existingData?.sources) && existingData.sources.length > 1) {
    console.log('Keeping existing manifest (', existingData.sources.length, 'sources) — source/ not available')
    process.exit(0)
  }
}
fs.writeFileSync(OUT, manifestStr)
const sizeKb = (manifestStr.length / 1024).toFixed(1)
console.log('Generated lib/sources-manifest.json:', sources.length, 'sources,', sizeKb, 'KB')
