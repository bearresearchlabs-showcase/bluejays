#!/usr/bin/env node
/**
 * dev:test — Start website with continuous sync and Qdrant stack.
 * 1. Kills any existing dev:test session (port 3000, watch-and-sync)
 * 2. Starts Docker Work API + Qdrant (if docker available)
 * 3. Runs initial sync + sync-to-qdrant
 * 4. Starts Next.js dev server
 * 5. Runs watch-and-sync in parallel (continuous sync + sync-to-qdrant on changes)
 */

const path = require('path')
const { spawn } = require('child_process')
const { execSync } = require('child_process')

const websiteDir = path.resolve(__dirname, '..')
const repoRoot = path.resolve(websiteDir, '../..')
const composeFile = path.join(repoRoot, 'docker', 'docker-compose.work-microservices.yml')
const WORK_API_URL = process.env.WORK_API_URL || 'http://localhost:8010'

function run(cmd, opts = {}) {
  try {
    execSync(cmd, { stdio: 'inherit', cwd: opts.cwd || websiteDir, env: { ...process.env, WORK_API_URL }, ...opts })
    return true
  } catch {
    return false
  }
}

function killExistingSession() {
  console.log('🛑 Killing existing dev:test session (port 3000)...')
  try {
    execSync('lsof -ti :3000 | xargs kill -9 2>/dev/null || true', { stdio: 'pipe', shell: true })
  } catch {}
  try {
    execSync('pkill -f "watch-and-sync.js" 2>/dev/null || true', { stdio: 'pipe', shell: true })
  } catch {}
}

killExistingSession()
function startDockerStack() {
  if (!require('fs').existsSync(composeFile)) return
  console.log('🐳 Starting Qdrant + Work API (Docker)...')
  run(`docker compose -f "${composeFile}" up -d`, { cwd: repoRoot })
}

function initialSync() {
  console.log('🔄 Initial sync (content + comprehensive-db)...')
  run('npm run sync-content')
  console.log('🔄 Syncing to Qdrant...')
  run(`WORK_API_URL=${WORK_API_URL} npm run sync-to-qdrant`)
}

startDockerStack()
initialSync()

// Spawn Next.js dev server
const nextProc = spawn('npx', ['next', 'dev', '-p', '3000'], {
  stdio: 'inherit',
  cwd: websiteDir,
  shell: false,
  env: { ...process.env, WORK_API_URL },
})

// Spawn watch-and-sync (continuous sync)
const watchProc = spawn('node', ['scripts/watch-and-sync.js'], {
  stdio: 'inherit',
  cwd: websiteDir,
  shell: false,
  env: { ...process.env, WORK_API_URL },
})

function killAll() {
  nextProc.kill('SIGTERM')
  watchProc.kill('SIGTERM')
  process.exit(0)
}

process.on('SIGINT', killAll)
process.on('SIGTERM', killAll)

nextProc.on('exit', (code) => {
  watchProc.kill('SIGTERM')
  process.exit(code ?? 0)
})
