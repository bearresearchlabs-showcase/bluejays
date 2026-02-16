#!/usr/bin/env node
/**
 * Sync website comprehensive-database.json to Qdrant via Work API.
 * Run after build-comprehensive-db when WORK_API_URL is set.
 *
 * Usage:
 *   WORK_API_URL=http://localhost:8010 node scripts/sync-to-qdrant.js
 *   npm run sync-to-qdrant
 */

const fs = require('fs')
const path = require('path')
const http = require('http')
const https = require('https')

const rootDir = path.join(__dirname, '..')
const comprehensivePath = path.join(rootDir, 'lib', 'comprehensive-database.json')
const WORK_API_URL = process.env.WORK_API_URL || process.env.WORK_API || 'http://localhost:8010'

function main() {
  if (!fs.existsSync(comprehensivePath)) {
    console.warn('⚠️  comprehensive-database.json not found. Run: npm run build-comprehensive-db')
    process.exit(0)
  }

  const data = JSON.parse(fs.readFileSync(comprehensivePath, 'utf-8'))
  const databases = data.databases || []
  if (databases.length === 0) {
    console.warn('⚠️  No databases in comprehensive-database.json')
    process.exit(0)
  }

  const body = JSON.stringify({ databases })
  const url = new URL(`${WORK_API_URL.replace(/\/$/, '')}/ingest/website`)
  const isHttps = url.protocol === 'https:'
  const lib = isHttps ? https : http

  const req = lib.request(
    {
      hostname: url.hostname,
      port: url.port || (isHttps ? 443 : 80),
      path: url.pathname,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    },
    (res) => {
      let buf = ''
      res.on('data', (ch) => { buf += ch })
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          const out = JSON.parse(buf || '{}')
          console.log(`✅ Synced to Qdrant: ${out.ingested || 0} queries from ${(out.sources || []).length} databases`)
        } else {
          console.error(`❌ Work API error: ${res.statusCode}`, buf)
          process.exit(1)
        }
      })
    }
  )
  req.on('error', (err) => {
    console.warn('⚠️  Work API unreachable:', err.message, '- is Qdrant Docker stack running?')
    process.exit(0)
  })
  req.write(body)
  req.end()
}

main()
