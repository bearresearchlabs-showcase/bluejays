import { readFileSync, existsSync, readdirSync } from 'fs'
import { join } from 'path'

// Vercel (Root Directory = apps/annotator): prebuild copies source/template into cwd
// Local dev: source/template live at repo root (cwd/../../)
function getRoot(): string {
  const cwd = process.cwd()
  const localSource = join(cwd, 'source')
  if (existsSync(localSource)) return cwd
  return join(cwd, '..', '..')
}
const ROOT = getRoot()

function sourceDir() {
  return join(ROOT, 'source')
}

function templateDir() {
  return join(ROOT, 'template')
}

export function discoverSources(): string[] {
  const sources = ['template']
  const src = sourceDir()
  if (!existsSync(src)) return sources

  const dirs = readdirSync(src, { withFileTypes: true })
    .filter((d) => d.isDirectory() && d.name.startsWith('db-'))
    .map((d) => d.name)
    .sort((a, b) => {
      const na = parseInt(a.replace('db-', ''), 10) || 999
      const nb = parseInt(b.replace('db-', ''), 10) || 999
      return na - nb
    })

  for (const name of dirs) {
    const base1 = join(src, name, 'app', 'QUERIES', 'queries.json')
    const base2 = join(src, name, 'QUERIES', 'queries.json')
    const base3 = join(ROOT, name, 'queries', 'queries.json')
    if (existsSync(base1) || existsSync(base2) || existsSync(base3)) {
      sources.push(name)
    }
  }
  return sources
}

function getQueriesPath(source: string): string | null {
  if (source.toLowerCase() === 'template') {
    const p = join(templateDir(), 'queries.json')
    return existsSync(p) ? p : null
  }
  const n = source.replace('db-', '').trim()
  const num = parseInt(n, 10)
  if (isNaN(num)) return null

  const bases = [
    join(sourceDir(), `db-${num}`, 'app', 'QUERIES', 'queries.json'),
    join(sourceDir(), `db-${num}`, 'QUERIES', 'queries.json'),
    join(ROOT, `db-${num}`, 'queries', 'queries.json'),
  ]
  for (const p of bases) {
    if (existsSync(p)) return p
  }
  return null
}

export function loadQueries(source: string): { queries: Record<string, unknown>[]; error?: string } {
  const path = getQueriesPath(source)
  if (!path) return { queries: [], error: `Not found: ${source}` }
  try {
    const raw = readFileSync(path, 'utf-8')
    const data = JSON.parse(raw)
    let queries: Record<string, unknown>[] = []
    if (Array.isArray(data)) {
      queries = data.filter((x): x is Record<string, unknown> => typeof x === 'object' && x !== null && 'question_id' in x)
    } else {
      queries = data?.queries ?? data?.data?.queries ?? []
    }
    return { queries }
  } catch (e) {
    return { queries: [], error: String(e) }
  }
}
