#!/usr/bin/env node
/**
 * AppSession logger - Log .mdc and repo changes to logs/AppSessions/ and telemetry.ndjson
 *
 * Usage:
 *   node scripts/app-session-logger.js [--mdc-changes "file1,file2"] [--repo-changes "path1,path2"] [--event "event_name"]
 *   node scripts/app-session-logger.js --from-git   # Infer from git diff (staged + unstaged)
 *
 * Writes:
 *   - logs/AppSessions/YYYYMMDD-HHMM-<sessionId>.ndjson
 *   - Appends to logs/telemetry.ndjson with component: "AppSession"
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

const ROOT = path.resolve(__dirname, '..')
const LOGS_DIR = path.join(ROOT, 'logs')
const APP_SESSIONS_DIR = path.join(LOGS_DIR, 'AppSessions')
const TELEMETRY_FILE = path.join(LOGS_DIR, 'telemetry.ndjson')

function timestamp() {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const h = String(now.getHours()).padStart(2, '0')
  const min = String(now.getMinutes()).padStart(2, '0')
  return `${y}${m}${d}-${h}${min}`
}

function sessionId() {
  return Math.random().toString(36).slice(2, 10)
}

function parseArgs() {
  const args = process.argv.slice(2)
  const out = { mdcChanges: [], repoChanges: [], event: 'session', fromGit: false }
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--mdc-changes' && args[i + 1]) {
      out.mdcChanges = args[++i].split(',').map(s => s.trim()).filter(Boolean)
    } else if (args[i] === '--repo-changes' && args[i + 1]) {
      out.repoChanges = args[++i].split(',').map(s => s.trim()).filter(Boolean)
    } else if (args[i] === '--event' && args[i + 1]) {
      out.event = args[++i]
    } else if (args[i] === '--from-git') {
      out.fromGit = true
    }
  }
  return out
}

function getGitDiffPaths() {
  try {
    const staged = execSync('git diff --name-only --cached 2>/dev/null || true', { cwd: ROOT, encoding: 'utf8' })
    const unstaged = execSync('git diff --name-only 2>/dev/null || true', { cwd: ROOT, encoding: 'utf8' })
    const all = new Set([...staged.split('\n'), ...unstaged.split('\n')].map(s => s.trim()).filter(Boolean))
    const mdc = [...all].filter(p => p.includes('.cursor/rules/') && p.endsWith('.mdc'))
    const repo = [...all].filter(p => p.startsWith('apps/') || p.startsWith('packages/'))
    return { mdcChanges: mdc, repoChanges: repo }
  } catch {
    return { mdcChanges: [], repoChanges: [] }
  }
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }
}

function writeNdjsonLine(filePath, obj) {
  fs.appendFileSync(filePath, JSON.stringify(obj) + '\n', 'utf8')
}

function main() {
  const opts = parseArgs()
  if (opts.fromGit) {
    const git = getGitDiffPaths()
    opts.mdcChanges = opts.mdcChanges.length ? opts.mdcChanges : git.mdcChanges
    opts.repoChanges = opts.repoChanges.length ? opts.repoChanges : git.repoChanges
  }

  const ts = timestamp()
  const sid = sessionId()
  const tsNum = Date.now() / 1000

  ensureDir(APP_SESSIONS_DIR)
  const sessionFile = path.join(APP_SESSIONS_DIR, `${ts}-${sid}.ndjson`)

  if (opts.mdcChanges.length > 0) {
    const entry = {
      ts: tsNum,
      sessionId: sid,
      event: 'mdc_updated',
      data: { files: opts.mdcChanges, changes: opts.mdcChanges },
    }
    writeNdjsonLine(sessionFile, entry)
    writeNdjsonLine(TELEMETRY_FILE, {
      ts: tsNum,
      component: 'AppSession',
      action: 'mdc_updated',
      status: 'ok',
      message: '',
      data: { sessionId: sid, files: opts.mdcChanges },
      duration_ms: 0,
    })
  }

  if (opts.repoChanges.length > 0) {
    const entry = {
      ts: tsNum,
      sessionId: sid,
      event: 'repo_changed',
      data: { paths: opts.repoChanges, action: opts.event },
    }
    writeNdjsonLine(sessionFile, entry)
    writeNdjsonLine(TELEMETRY_FILE, {
      ts: tsNum,
      component: 'AppSession',
      action: 'repo_changed',
      status: 'ok',
      message: '',
      data: { sessionId: sid, paths: opts.repoChanges },
      duration_ms: 0,
    })
  }

  if (opts.mdcChanges.length === 0 && opts.repoChanges.length === 0) {
    const entry = {
      ts: tsNum,
      sessionId: sid,
      event: opts.event,
      data: {},
    }
    writeNdjsonLine(sessionFile, entry)
  }

  console.log(`AppSession logged: ${sessionFile}`)
}

main()
