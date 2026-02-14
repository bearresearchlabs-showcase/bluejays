import { readFileSync, existsSync, readdirSync } from 'fs'
import { join } from 'path'

// Build-time manifest (static import ensures bundling on Vercel)
import manifestJson from './sources-manifest.json'

type Manifest = { sources?: string[]; queries?: Record<string, unknown[]> }
const manifest = manifestJson as Manifest
const manifestSources: string[] | null =
  Array.isArray(manifest.sources) && manifest.sources.length > 1 ? manifest.sources : null

// Annotator at repo root: source/ and template/ are siblings of app/
function getRoot(): string {
  return process.cwd()
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
  if (existsSync(src)) {
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
  }
  // Vercel: prefer build-time manifest when it has more sources (fs may be empty/partial)
  if (manifestSources && manifestSources.length > sources.length) return manifestSources
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
  const filePath = getQueriesPath(source)
  if (filePath) {
    try {
      const raw = readFileSync(filePath, 'utf-8')
      const data = JSON.parse(raw)
      let queries: Record<string, unknown>[] = []
      if (Array.isArray(data)) {
        queries = data.filter((x): x is Record<string, unknown> => typeof x === 'object' && x !== null && ('question_id' in x || 'question' in x || 'sql' in x || 'number' in x || 'title' in x))
      } else {
        queries = (data?.queries ?? data?.data?.queries ?? []) as Record<string, unknown>[]
      }
      return { queries }
    } catch (e) {
      return { queries: [], error: String(e) }
    }
  }
  // Vercel: use embedded manifest when filesystem unavailable
  const queriesFromManifest = manifest.queries?.[source]
  if (Array.isArray(queriesFromManifest) && queriesFromManifest.length > 0) {
    const q = queriesFromManifest.filter((x): x is Record<string, unknown> =>
      typeof x === 'object' && x !== null && ('question_id' in x || 'question' in x || 'sql' in x || 'number' in x || 'title' in x)
    )
    return { queries: q }
  }
  return { queries: [], error: `Not found: ${source}` }
}
